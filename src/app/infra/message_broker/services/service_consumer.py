from functools import lru_cache
from src.app.infra.message_broker.interfaces.consumer_service import ConsumerService

from src.app.infra.message_broker.contracts.kafka_consumer_adapter_v0 import (
    KafkaConsumerAdapter,
)


@lru_cache(maxsize=1)
def get_service_consumer() -> ConsumerService:
    return KafkaConsumerAdapter()
