from functools import lru_cache
import asyncio
import threading
from abc import ABC
from confluent_kafka import Consumer, KafkaError, Producer
from src.app.infra.message_broker.entities.abstract_consumer_adapter import (
    AbstractConsumerAdapter,
)
from src.app.infra.events.entities.event import Event
from src.app.infra.events.features.process_events.schemas.INPUT_ProcessEvents import (
    INPUT_ProcessEvents,
)
from src.app.infra.events.features.process_events.services.SERVICE_ProcessEvents import (
    SERVICE_ProcessEvents,
)
from src.app.infra.logger.services.service_logger import get_service_logger
from src.app.infra.dotenv.services.service_dotenv import get_service_dotenv
import json

logger = get_service_logger()
dotenv = get_service_dotenv()


class KafkaConsumerAdapter(AbstractConsumerAdapter, ABC):
    def __init__(self):
        super().__init__(logger)
        self.conf = {
            "bootstrap.servers": "localhost:9092",
            "group.id": "order-processing-group",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": True,
        }
        self.topic = ["order-events"]
        self.dlq_topic = "orders-dlq"
        self.logger = logger
        self.keep_running = False

    def init(self):
        try:
            self.consumer = Consumer(self.conf)
            self.consumer.subscribe(self.topic)
            self.producer = Producer(self.conf)  # need to develop this properly
            self.logger.info("Kafka consumer initialized successfully.")
        except KafkaError as e:
            self.logger.error(f"Error reconnecting to Kafka: {e}")
            raise e

    def before_starting_poll(self):
        self.keep_running = True

    def after_starting_poll(self):
        pass  # Placeholder for potential post-poll actions

    def before_stopping_poll(self):
        self.keep_running = False
        self.disconnect_consumer(True)

    def after_stopping_poll(self):
        pass  # Placeholder for potential post-stop actions

    def poll_messages(self):
        try:
            self.init()
            self.keep_running = True
            while self.keep_running:

                msg = self.consumer.poll(timeout=1.0)

                if msg is None:
                    continue
                self.logger.warning("number of messages from kafka")
                # logger.warning(self.consumer)
                self.logger.warning(msg)

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        self.logger.info(
                            f"Reached end of partition for {msg.topic()} [{msg.partition()}] at offset {msg.offset()}"
                        )
                    elif msg.error():
                        self.logger.error(f"Kafka error: {msg.error()}")
                        break
                else:
                    try:
                        asyncio.run(
                            self._consume_message(
                                key=msg.key().decode("utf-8") if msg.key() else None,
                                value=json.loads(msg.value().decode("utf-8")),
                            )
                        )
                    except Exception as e:
                        self.logger.error(
                            f"Error processing message, sending to DLQ: {str(e)}"
                        )
                        self.producer.produce(
                            self.dlq_topic, key=msg.key(), value=msg.value()
                        )
                        self.producer.flush()
        except Exception as e:
            self.logger.error(f"Unexpected error in Kafka consumer: {str(e)}")
            raise e
        finally:
            self.consumer.close()
            self.logger.info("Kafka consumer closed")

    def disconnect_consumer(self, commit_offsets=True):
        try:
            if commit_offsets:
                # Commit the current offsets (if manual commit)
                self.consumer.commit()
                self.logger.info("Offsets committed.")

            # Close the consumer, releasing any resources
            self.consumer.close()
            self.logger.warning("Kafka consumer closed successfully.")
        except KafkaError as e:
            self.logger.error(f"Error during consumer disconnection: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error during disconnection: {e}")

    async def _consume_message(self, key, value):
        try:
            event = Event(
                id=value.get("id"), name=value.get("name"), data=value.get("data")
            )
            self.logger.info(event)
            request = INPUT_ProcessEvents(event=event)
            result = await SERVICE_ProcessEvents(request)
            self.logger.info(f"Processed event: {result.message}")
        except Exception as e:
            self.logger.error(f"Error processing message, sending to DLQ: {str(e)}")
            self.producer.produce(self.dlq_topic, key=key, value=value)
            self.producer.flush()
