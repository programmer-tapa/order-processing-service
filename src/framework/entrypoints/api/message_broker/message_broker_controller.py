import json
from fastapi import APIRouter, Request, Response, Depends
from src.app.infra.message_broker.functions.start_consume_message_from_kafka import (
    FUNCTION_start_consume_message_from_kafka,
)
from src.app.infra.message_broker.functions.stop_consume_message_from_kafka import (
    FUNCTION_stop_consume_message_from_kafka,
)
from src.app.infra.logger.services.service_logger import get_service_logger
from src.app.infra.dotenv.services.service_dotenv import get_service_dotenv

logger = get_service_logger()


router = APIRouter()


@router.post("/start_consuming_message")
async def start_consuming(request: Request):
    try:
        body = await request.body()
        data = json.loads(body) if body else {}
    except json.JSONDecodeError:
        data = {}
    response = FUNCTION_start_consume_message_from_kafka(data)
    return str(response)


@router.post("/stop_consuming_message")
async def stop_consuming(request: Request):
    try:
        body = await request.body()
        data = json.loads(body) if body else {}
    except json.JSONDecodeError:
        data = {}
    response = FUNCTION_stop_consume_message_from_kafka(data)
    return str(response)
