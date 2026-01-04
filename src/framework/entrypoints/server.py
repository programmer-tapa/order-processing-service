# from src.framework.middlewares.route_error_handler import route_error_handler
from src.framework.middlewares.route_error_handler import RouteErrorHandlerMiddleware
import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from src.framework.entrypoints.api.routes import api_router
from src.app.infra.dotenv.services.service_dotenv import get_service_dotenv
from src.app.infra.logger.services.service_logger import get_service_logger


dotenv = get_service_dotenv()
logger = get_service_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):

    from src.app.infra.message_broker.functions.start_consume_message_from_kafka import (
        FUNCTION_start_consume_message_from_kafka,
    )

    try:
        logger.debug(
            "---------------------------------------------------------------------------"
        )
        logger.debug(
            "---------------------------------------------------------------------------"
        )
        logger.debug(
            "---------------------------------------------------------------------------"
        )
        logger.debug("startup -> start_consume_message_from_kafka : begins")
        logger.debug(
            "---------------------------------------------------------------------------"
        )
        FUNCTION_start_consume_message_from_kafka(None)
        logger.debug(
            "---------------------------------------------------------------------------"
        )
        logger.debug("startup -> start_consume_message_from_kafka : completes")
        logger.debug(
            "---------------------------------------------------------------------------"
        )
    except Exception as e:
        logger.error(
            f"start_consume_message_from_kafka could not be started due to : {e}"
        )
    finally:
        logger.info(
            ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> -------------------- startup run"
        )

    yield

    from src.app.infra.message_broker.functions.stop_consume_message_from_kafka import (
        FUNCTION_stop_consume_message_from_kafka,
    )

    try:
        logger.debug(
            "---------------------------------------------------------------------------"
        )
        logger.debug("shutdown -> stop_consume_message_from_kafka : begins")
        logger.debug(
            "---------------------------------------------------------------------------"
        )
        FUNCTION_stop_consume_message_from_kafka(None)
        logger.debug(
            "---------------------------------------------------------------------------"
        )
        logger.debug("shutdown -> stop_consume_message_from_kafka : completes")
        logger.debug(
            "---------------------------------------------------------------------------"
        )
        logger.debug(
            "---------------------------------------------------------------------------"
        )
        logger.debug(
            "---------------------------------------------------------------------------"
        )
    except Exception as e:
        logger.error(f"something went wrong in stop_consume_message_from_kafka : {e}")
    finally:
        logger.info(
            ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> -------------------- shutdown run"
        )


"""
Create APP and Attache API routes
"""
app = FastAPI(
    lifespan=lifespan,
    title=dotenv.APP_NAME,
    openapi_url=dotenv.OPENAPI_URL if not dotenv.PRODUCTION_ENV else None,
)


app.include_router(api_router, prefix=dotenv.API_V1_STR)


from src.framework.middlewares.debugger import DebuggerMiddleware

app.add_middleware(DebuggerMiddleware)

"""
GZipMiddleware
Handles GZip responses for any request that includes "gzip" in the Accept-Encoding header.
The middleware will handle both standard and streaming responses.
"""
if dotenv.APP_MIDDLEWARE_GZIP:
    logger.info("Adding GZipMiddleware")
    from fastapi.middleware.gzip import GZipMiddleware

    app.add_middleware(GZipMiddleware, minimum_size=1000)


"""
CORSMiddleware
Set all CORS enabled origins
"""
if dotenv.APP_MIDDLEWARE_CORS:
    from starlette.middleware.cors import CORSMiddleware

    logger.info(f"Allowed origins for CORS: {dotenv.BACKEND_CORS_ORIGINS}")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=dotenv.BACKEND_CORS_ORIGINS,
        allow_credentials=dotenv.BACKEND_CORS_CREDENTIALS,
        allow_methods=dotenv.BACKEND_CORS_METHODS,
        allow_headers=dotenv.BACKEND_CORS_HEADERS,
        expose_headers=["Content-Type"],
    )

"""
TrustedHostMiddleware
Enforces that all incoming requests have a correctly set Host header, in order to guard against HTTP Host Header attacks.
"""
if dotenv.APP_MIDDLEWARE_TRUSTEDHOST:
    from fastapi.middleware.trustedhost import TrustedHostMiddleware

    allowed_hosts = dotenv.BACKEND_ALLOWED_HOSTS
    logger.info(f"Allowed hosts for TrustedHostMiddleware: {allowed_hosts}")
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

"""
HTTPSRedirectMiddleware
Enforces that all incoming requests must either be https or wss.
Any incoming requests to http or ws will be redirected to the secure scheme instead.
"""
if dotenv.APP_MIDDLEWARE_HTTPSREDIRECT:
    from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

    app.add_middleware(HTTPSRedirectMiddleware)

# This is the last middleware to be added, it should be the last one in the list
app.add_middleware(RouteErrorHandlerMiddleware)
