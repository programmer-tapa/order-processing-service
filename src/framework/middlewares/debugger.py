import traceback
import json
from fastapi import Request, Response
from src.app.infra.logger.services.service_logger import get_service_logger
from starlette.middleware.base import BaseHTTPMiddleware

logger = get_service_logger()


class DebuggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        funcName = "MIDDLEWARE : debugger"
        logger.info(funcName)
        try:
            response = await call_next(request)
        except Exception as e:
            logger.warning(funcName + " - " + str(e))
            var = traceback.format_exc()
            logger.debug(var)
        else:
            return response
