"""
Base exception for application-specific errors that map to a ServiceStatus.

This is the abstract base class for all custom application exceptions.
"""

from src.app.core.origin.schemas.ServiceStatus import ServiceStatus


class AppException(Exception):
    """
    Base exception for application-specific errors.

    Attributes:
        status: The ServiceStatus indicating the type of error
        message: Human-readable error message
    """

    def __init__(self, status: ServiceStatus, message: str):
        super().__init__(message)
        self._status = status

    @property
    def status(self) -> ServiceStatus:
        """Get the ServiceStatus for this exception."""
        return self._status
