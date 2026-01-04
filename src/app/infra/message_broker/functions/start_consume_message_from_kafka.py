from src.app.infra.logger.services.service_logger import get_service_logger
from src.app.infra.dotenv.services.service_dotenv import get_service_dotenv
from src.app.infra.message_broker.services.service_consumer import get_service_consumer

consumer_adapter = get_service_consumer()


def FUNCTION_start_consume_message_from_kafka(data):
    response = consumer_adapter.start_scheduler()
    return response
