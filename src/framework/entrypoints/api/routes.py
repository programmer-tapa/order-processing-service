from fastapi import APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from src.framework.entrypoints.api.message_broker.message_broker_controller import (
    router as message_broker_router,
)
from src.app.infra.logger.services.service_logger import get_service_logger
from src.app.infra.dotenv.services.service_dotenv import get_service_dotenv

dotenv = get_service_dotenv()

api_router = APIRouter()
api_router.include_router(
    message_broker_router, prefix="/message_broker", tags=["message_broker"]
)
