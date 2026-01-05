"""
Interface for usecase authorization service.

Mirrors the Java UsecaseAuthorizationService interface from order-service.
"""

from abc import ABC, abstractmethod

from src.app.core.origin.schemas.User import User


class UsecaseAuthorizationService(ABC):
    """
    Interface for authorizing users to execute use cases.

    Implementations should check if a user has the necessary permissions
    to execute a specific service/usecase.
    """

    @abstractmethod
    def is_authorized(self, user: User, service_name: str) -> bool:
        """
        Check if the user is authorized to execute the given service.

        Args:
            user: The user to authorize
            service_name: The unique identifier of the service/usecase

        Returns:
            True if the user is authorized, False otherwise
        """
        pass
