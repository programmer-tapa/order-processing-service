"""
Abstract service that handles authorization and usecase execution.

Mirrors the Java AbstractService class from order-service.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from src.app.core.origin.entities.abstract_usecase import AbstractUsecase
from src.app.core.origin.exceptions.AppException import AppException
from src.app.core.origin.schemas.ServiceDependency import ServiceDependency
from src.app.core.origin.schemas.ServiceInput import ServiceInput
from src.app.core.origin.schemas.ServiceOutput import ServiceOutput
from src.app.core.origin.schemas.User import User

I = TypeVar("I")  # Input type
O = TypeVar("O")  # Output type


class AbstractService(ABC, Generic[I, O]):
    """
    Abstract service that handles authorization and usecase execution.

    This class provides:
    - Authorization via UsecaseAuthorizationService
    - Structured input/output via ServiceInput/ServiceOutput
    - Exception handling with proper status mapping

    Subclasses must implement:
    - detect_service_name(): Return a unique service identifier
    - build(): Create the usecase instance with its dependencies
    """

    def __init__(self, dependencies: ServiceDependency):
        """
        Constructor to inject service dependencies.

        Args:
            dependencies: The container holding all service dependencies
        """
        self.authorization_service = dependencies.authorization_service

    @abstractmethod
    def detect_service_name(self) -> str:
        """
        Detect and return the service name.
        Used for authorization and logging purposes.

        Returns:
            The unique name/identifier of this service
        """
        pass

    @abstractmethod
    def build(self, input_data: I) -> AbstractUsecase:
        """
        Build the usecase with its dependencies.

        Args:
            input_data: The usecase input, can be used to determine and fetch
                        the right dependencies based on input values.

        Returns:
            The configured usecase instance
        """
        pass

    def authorize(self, user: User) -> bool:
        """
        Authorize the user for this usecase.
        Uses the authorization service to check if the user is authorized.

        Args:
            user: The user to authorize

        Returns:
            True if authorized, False otherwise
        """
        if user is None:
            return True
        if self.authorization_service is None:
            # No authorization service configured - allow all
            return True
        service_name = self.detect_service_name()
        return self.authorization_service.is_authorized(user, service_name)

    async def run(self, service_input: ServiceInput[I]) -> ServiceOutput[O]:
        """
        Run the service with authorization and structured response.

        Args:
            service_input: The service input containing user and data

        Returns:
            ServiceOutput with status, data, and error message
        """
        # Authorization check
        if not self.authorize(service_input.user):
            return ServiceOutput.unauthorized(
                "User is not authorized to perform this action"
            )

        # Build and execute usecase
        try:
            # Decouple service orchestration from business logic by using
            # a factory method to build the usecase, allowing for dynamic
            # dependency injection based on input.
            usecase = self.build(service_input.data)
            result = await usecase.execute(service_input.data)
            return ServiceOutput.success(result)
        except AppException as e:
            return ServiceOutput(status=e.status, data=None, error_message=str(e))
        except Exception as e:
            return ServiceOutput.failure(str(e))
