"""
ServiceStatus enum for categorizing error types.

Mirrors the Java ServiceStatus enum from order-service.
"""

from enum import Enum


class ServiceStatus(Enum):
    """Enum representing the status of service execution."""

    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    UNAUTHORIZED = "UNAUTHORIZED"
    NOT_FOUND = "NOT_FOUND"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    CONFLICT = "CONFLICT"
    INTERNAL_ERROR = "INTERNAL_ERROR"
