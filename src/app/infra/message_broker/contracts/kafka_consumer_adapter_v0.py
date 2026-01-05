"""
Kafka Consumer Adapter with failsafe mechanisms.

Provides reliable Kafka message consumption with:
- Connection retry with exponential backoff
- Safe JSON deserialization
- Correlation ID tracing
- Robust DLQ handling
- Graceful shutdown
"""

import asyncio
import json
import threading
import uuid
from abc import ABC
from typing import Optional

from confluent_kafka import Consumer, KafkaError, Producer

from src.app.infra.message_broker.entities.abstract_consumer_adapter import (
    AbstractConsumerAdapter,
)
from src.app.infra.events.entities.event import Event
from src.app.infra.events.features.process_events.schemas.INPUT_ProcessEvents import (
    INPUT_ProcessEvents,
)
from src.app.infra.events.features.process_events.factory.FUNCTION_ProcessEvents import (
    FUNCTION_ProcessEvents,
)
from src.app.infra.events.features.process_events.schemas.OUTPUT_ProcessEvents import (
    OUTPUT_ProcessEvents,
)
from src.app.infra.logger.services.service_logger import get_service_logger
from src.app.infra.dotenv.services.service_dotenv import get_service_dotenv

logger = get_service_logger()
dotenv = get_service_dotenv()


class KafkaConsumerAdapter(AbstractConsumerAdapter, ABC):
    """
    Kafka consumer adapter with failsafe mechanisms.

    Features:
    - Automatic connection retry with exponential backoff
    - Safe JSON deserialization with DLQ routing for invalid messages
    - Correlation ID generation for distributed tracing
    - Graceful shutdown handling
    - Thread-safe consumer lifecycle
    """

    # Configuration
    MAX_CONNECTION_RETRIES = 5
    INITIAL_BACKOFF_SECONDS = 1
    MAX_BACKOFF_SECONDS = 30

    def __init__(self):
        super().__init__(logger)
        self.conf = {
            "bootstrap.servers": dotenv.KAFKA_BROKER_URL,
            "group.id": dotenv.KAFKA_GROUP_ID,
            "auto.offset.reset": dotenv.KAFKA_AUTO_OFFSET_RESET,
            "enable.auto.commit": True,
        }
        self.topic = dotenv.KAFKA_TOPIC
        self.dlq_topic = dotenv.KAFKA_DLQ_TOPIC
        self.logger = logger
        self.keep_running = False
        self._consumer: Optional[Consumer] = None
        self._producer: Optional[Producer] = None
        self._consumer_closed = True

    def init(self):
        """
        Initialize Kafka consumer and producer with retry logic.

        Implements exponential backoff for connection failures.
        Raises ConnectionError after MAX_CONNECTION_RETRIES attempts.
        """
        backoff = self.INITIAL_BACKOFF_SECONDS

        for attempt in range(1, self.MAX_CONNECTION_RETRIES + 1):
            try:
                self.logger.info(
                    f"Connecting to Kafka (attempt {attempt}/{self.MAX_CONNECTION_RETRIES})..."
                )
                self._consumer = Consumer(self.conf)
                self._consumer.subscribe(self.topic)
                self._producer = Producer(
                    {"bootstrap.servers": dotenv.KAFKA_BROKER_URL}
                )
                self._consumer_closed = False
                self.logger.info("Kafka consumer initialized successfully.")
                return
            except KafkaError as e:
                self.logger.error(f"Kafka connection failed (attempt {attempt}): {e}")
                if attempt == self.MAX_CONNECTION_RETRIES:
                    raise ConnectionError(
                        f"Failed to connect to Kafka after {self.MAX_CONNECTION_RETRIES} attempts"
                    )
                self.logger.info(f"Retrying in {backoff}s...")
                # Interruptible sleep
                for _ in range(backoff):
                    if self.stop_flag.is_set():
                        raise InterruptedError("Connection interrupted by shutdown")
                    import time

                    time.sleep(1)
                backoff = min(backoff * 2, self.MAX_BACKOFF_SECONDS)

    def before_starting_poll(self):
        self.keep_running = True

    def after_starting_poll(self):
        pass

    def before_stopping_poll(self):
        self.keep_running = False

    def after_stopping_poll(self):
        self._close_consumer(commit_offsets=True)

    def poll_messages(self):
        """
        Main polling loop with failsafe error handling.

        Handles:
        - Kafka errors gracefully
        - JSON deserialization failures → DLQ
        - Processing failures → DLQ
        - Clean shutdown on stop signal
        """
        try:
            self.init()

            while self.keep_running and not self.stop_flag.is_set():
                msg = self._consumer.poll(timeout=1.0)

                if msg is None:
                    continue

                # Generate correlation ID for this message
                correlation_id = str(uuid.uuid4())[:8]

                if msg.error():
                    self._handle_kafka_error(msg, correlation_id)
                    continue

                # Safe message processing
                self._process_message_safely(msg, correlation_id)

        except InterruptedError:
            self.logger.info("Poll interrupted by shutdown signal")
        except Exception as e:
            self.logger.error(f"Unexpected error in Kafka consumer: {str(e)}")
            raise
        finally:
            self._close_consumer(commit_offsets=True)

    def _handle_kafka_error(self, msg, correlation_id: str):
        """Handle Kafka-level errors."""
        error = msg.error()
        if error.code() == KafkaError._PARTITION_EOF:
            self.logger.debug(
                f"[{correlation_id}] Reached end of partition for "
                f"{msg.topic()} [{msg.partition()}] at offset {msg.offset()}"
            )
        else:
            self.logger.error(f"[{correlation_id}] Kafka error: {error}")

    def _process_message_safely(self, msg, correlation_id: str):
        """
        Process a message with comprehensive error handling.

        All failures result in DLQ routing to prevent message loss.
        """
        raw_value = None
        try:
            # Step 1: Decode message
            raw_value = msg.value()
            key = msg.key().decode("utf-8") if msg.key() else None

            # Step 2: Parse JSON (can fail for invalid messages)
            try:
                value = json.loads(raw_value.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                self.logger.error(
                    f"[{correlation_id}] Invalid JSON/encoding in message: {e}"
                )
                self._send_to_dlq(
                    msg.key(), raw_value, correlation_id, f"JSON error: {e}"
                )
                return

            # Step 3: Process the event
            self.logger.info(
                f"[{correlation_id}] Processing message: {value.get('name', 'unknown')}"
            )
            asyncio.run(self._consume_message(key, value, correlation_id))

        except Exception as e:
            self.logger.error(f"[{correlation_id}] Error processing message: {str(e)}")
            self._send_to_dlq(
                msg.key(), raw_value or msg.value(), correlation_id, str(e)
            )

    def _send_to_dlq(self, key, value, correlation_id: str, error_reason: str):
        """
        Send failed message to Dead Letter Queue with error metadata.

        Handles DLQ producer failures gracefully.
        """
        try:
            # Add error metadata as headers
            headers = [
                ("correlation_id", correlation_id.encode("utf-8")),
                (
                    "error_reason",
                    error_reason[:500].encode("utf-8"),
                ),  # Truncate long errors
            ]

            self._producer.produce(
                self.dlq_topic, key=key, value=value, headers=headers
            )
            self._producer.flush(timeout=5)
            self.logger.warning(
                f"[{correlation_id}] Message sent to DLQ: {self.dlq_topic}"
            )
        except Exception as dlq_error:
            # Critical: DLQ failed, log extensively for manual recovery
            self.logger.critical(
                f"[{correlation_id}] CRITICAL: Failed to send to DLQ! "
                f"DLQ Error: {dlq_error}. Original error: {error_reason}. "
                f"Message key: {key}"
            )

    def _close_consumer(self, commit_offsets: bool = True):
        """
        Close consumer safely, preventing double-close errors.
        """
        if self._consumer_closed:
            return

        try:
            if commit_offsets and self._consumer:
                try:
                    self._consumer.commit()
                    self.logger.info("Offsets committed.")
                except KafkaError as e:
                    self.logger.warning(f"Could not commit offsets: {e}")

            if self._consumer:
                self._consumer.close()
                self.logger.info("Kafka consumer closed successfully.")
        except Exception as e:
            self.logger.error(f"Error during consumer disconnection: {e}")
        finally:
            self._consumer_closed = True

    def disconnect_consumer(self, commit_offsets: bool = True):
        """Public method to disconnect consumer (for backward compatibility)."""
        self._close_consumer(commit_offsets)

    async def _consume_message(
        self, key: Optional[str], value: dict, correlation_id: str
    ):
        """
        Process a validated message through the event pipeline.

        Raises exception on failure to trigger DLQ routing.
        """
        try:
            event = Event(
                id=value.get("id"), name=value.get("name"), data=value.get("data")
            )
            self.logger.info(f"[{correlation_id}] Event: {event.name} (ID: {event.id})")

            request = INPUT_ProcessEvents(event=event)
            result: OUTPUT_ProcessEvents = await FUNCTION_ProcessEvents(request)

            if not result.success:
                raise RuntimeError(f"Event processing failed: {result.message}")

            self.logger.info(
                f"[{correlation_id}] Processed successfully: {result.message}"
            )
        except Exception as e:
            self.logger.error(f"[{correlation_id}] Event processing error: {str(e)}")
            raise  # Re-raise to trigger DLQ routing
