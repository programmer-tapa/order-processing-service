"""
Generic service output wrapper with status, data, and error message.

Mirrors the Java ServiceOutput record from order-service.
"""

from dataclasses import dataclass
from typing import Generic, TypeVar, Optional

from src.app.core.origin.schemas.ServiceStatus import ServiceStatus

O = TypeVar("O")


@dataclass
class ServiceOutput(Generic[O]):
    """
    Generic service output wrapper with status, data, and error message.

    Attributes:
        status: The status of the service execution
        data: The usecase output data (None on error)
        error_message: Human-readable error message (None on success)
    """

    status: ServiceStatus
    data: Optional[O]
    error_message: Optional[str]

    @classmethod
    def success(cls, data: O) -> "ServiceOutput[O]":
        """Create a successful response."""
        return cls(status=ServiceStatus.SUCCESS, data=data, error_message=None)

    @classmethod
    def failure(cls, error_message: str) -> "ServiceOutput[O]":
        """Create a failure response."""
        return cls(status=ServiceStatus.FAILURE, data=None, error_message=error_message)

    @classmethod
    def unauthorized(cls, error_message: str) -> "ServiceOutput[O]":
        """Create an unauthorized response."""
        return cls(
            status=ServiceStatus.UNAUTHORIZED, data=None, error_message=error_message
        )

    @classmethod
    def not_found(cls, error_message: str) -> "ServiceOutput[O]":
        """Create a not found response."""
        return cls(
            status=ServiceStatus.NOT_FOUND, data=None, error_message=error_message
        )

    @classmethod
    def validation_error(cls, error_message: str) -> "ServiceOutput[O]":
        """Create a validation error response."""
        return cls(
            status=ServiceStatus.VALIDATION_ERROR,
            data=None,
            error_message=error_message,
        )

    @classmethod
    def conflict(cls, error_message: str) -> "ServiceOutput[O]":
        """Create a conflict response."""
        return cls(
            status=ServiceStatus.CONFLICT, data=None, error_message=error_message
        )

    @classmethod
    def internal_error(cls, error_message: str) -> "ServiceOutput[O]":
        """Create an internal error response."""
        return cls(
            status=ServiceStatus.INTERNAL_ERROR, data=None, error_message=error_message
        )
