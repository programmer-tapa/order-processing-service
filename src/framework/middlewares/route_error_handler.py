import traceback
import json
from fastapi import Request, Response
from src.framework.helpers.api_response import ErrorResponse
from src.app.infra.dotenv.services.service_dotenv import get_service_dotenv
from src.app.infra.logger.services.service_logger import get_service_logger
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


dotenv = get_service_dotenv()
logger = get_service_logger()


class RouteErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response: Response = await call_next(request)
            return response
        except Exception as e:
            route_path = request.url.path
            error_message = f"Error at route - {route_path} : {str(e)}"
            logger.error(error_message)
            errorReponse = ErrorResponse(message=error_message, error_code="500")
            return JSONResponse(content=errorReponse.__dict__, status_code=500)
