"""
Exception raised when an order is not found.
"""

from src.app.core.origin.exceptions.AppException import AppException
from src.app.core.origin.schemas.ServiceStatus import ServiceStatus


class OrderNotFoundException(AppException):
    """Exception raised when an order cannot be found by ID."""

    def __init__(self, message: str):
        super().__init__(ServiceStatus.NOT_FOUND, message)
