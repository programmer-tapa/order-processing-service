"""
Exception raised when order validation fails.
"""

from src.app.core.origin.exceptions.AppException import AppException
from src.app.core.origin.schemas.ServiceStatus import ServiceStatus


class InvalidOrderException(AppException):
    """Exception raised when an order is not in a valid state for processing."""

    def __init__(self, message: str):
        super().__init__(ServiceStatus.VALIDATION_ERROR, message)
