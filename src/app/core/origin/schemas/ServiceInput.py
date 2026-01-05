"""
Generic service input wrapper that encapsulates user context and usecase input.

Mirrors the Java ServiceInput record from order-service.
"""

from dataclasses import dataclass
from typing import Generic, TypeVar, Optional

from src.app.core.origin.schemas.User import User

I = TypeVar("I")


@dataclass
class ServiceInput(Generic[I]):
    """
    Generic service input wrapper that encapsulates user context and usecase input.

    Attributes:
        user: The user making the request (can be None for unauthenticated requests)
        data: The usecase-specific input data
    """

    user: Optional[User]
    data: I
