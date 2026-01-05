"""
User schema for representing the current user context.

Mirrors the Java User class from order-service.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """
    Represents a user in the system.

    Attributes:
        id: Unique identifier for the user
        username: The user's username
        roles: List of roles assigned to the user
    """

    id: str
    username: str
    roles: Optional[list[str]] = None
