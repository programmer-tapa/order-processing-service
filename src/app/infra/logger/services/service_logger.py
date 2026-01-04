from functools import lru_cache
from src.app.infra.logger.interfaces.logger_service import LoggerService

from src.app.infra.logger.contracts.logger_service_contract_v0 import (
    LoggerServiceContractV0,
)


@lru_cache(maxsize=1)
def get_service_logger() -> LoggerService:
    return LoggerServiceContractV0()
