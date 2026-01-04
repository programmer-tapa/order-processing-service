from typing import Any, List
from pydantic_settings import BaseSettings


class DotEnv(BaseSettings):

    PRODUCTION_ENV: bool

    """
    Settings for Uvicorn
    """
    APP_NAME: str
    APP_HOST: str  # for Uvicorn
    APP_PORT: int  # for Uvicorn
    APP_RELOAD: bool  # for Uvicorn

    API_V1_STR: str  # part of URL route could be configured with reverse-proxy route
    OPENAPI_URL: str  # part of URL route used to load API documentation
    LOG_FILE: str  # name of log file

    """
    Settings to enable or disable Middlewares
    """
    APP_MIDDLEWARE_CORS: bool  # enables or disables CORS
    APP_MIDDLEWARE_GZIP: bool  # enables or disables GZIP
    APP_MIDDLEWARE_TRUSTEDHOST: bool  # enables or disables TrustedHost
    APP_MIDDLEWARE_HTTPSREDIRECT: bool  # enables or disables HttpsDirect

    BACKEND_CORS_ORIGINS: List
    BACKEND_CORS_CREDENTIALS: bool
    BACKEND_CORS_METHODS: List
    BACKEND_CORS_HEADERS: List

    BACKEND_ALLOWED_HOSTS: List

    KAFKA_BROKER_URL: str
    KAFKA_GROUP_ID: str
    KAFKA_TOPIC: List[str]
    KAFKA_DLQ_TOPIC: str
    KAFKA_AUTO_OFFSET_RESET: str

    class Config:
        env_file = ".env"
