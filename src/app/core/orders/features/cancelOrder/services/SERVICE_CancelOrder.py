"""
Service for cancelling orders.

Mirrors the Java SERVICE_CreateOrder class architecture from order-service.
"""

from typing import Dict

from src.app.core.orders.features.cancelOrder.interfaces.INTERFACE_HELPER_CancelOrder import (
    INTERFACE_HELPER_CancelOrder,
)
from src.app.core.orders.features.cancelOrder.usecases.USECASE_CancelOrder import (
    USECASE_CancelOrder,
)
from src.app.core.orders.features.cancelOrder.schemas.INPUT_CancelOrder import (
    INPUT_CancelOrder,
)
from src.app.core.orders.features.cancelOrder.schemas.OUTPUT_CancelOrder import (
    OUTPUT_CancelOrder,
)
from src.app.core.origin.entities.abstract_service import AbstractService
from src.app.core.origin.entities.abstract_usecase import AbstractUsecase
from src.app.core.origin.schemas.ServiceDependency import ServiceDependency
from src.app.infra.logger.services.service_logger import get_service_logger


class SERVICE_CancelOrder(AbstractService[INPUT_CancelOrder, OUTPUT_CancelOrder]):
    """
    Service for cancelling orders.

    Handles authorization, builds the usecase with appropriate helpers,
    and provides structured input/output handling.
    """

    SERVICE_NAME = "Orders.CancelOrder"

    def __init__(
        self,
        dependencies: ServiceDependency,
        helpers: Dict[str, INTERFACE_HELPER_CancelOrder],
    ):
        """
        Initialize the service with dependencies and helpers.

        Args:
            dependencies: Container with shared service dependencies
            helpers: Map of helper key to implementation (e.g., "CONTRACT_HELPER_CancelOrder_V0")
        """
        super().__init__(dependencies)
        self.helpers = helpers
        self.logger = get_service_logger()

    def detect_service_name(self) -> str:
        """Return the service name for authorization and logging."""
        return self.SERVICE_NAME

    def build(self, input_data: INPUT_CancelOrder) -> AbstractUsecase:
        """
        Build the usecase with its dependencies.

        Selects the appropriate helper implementation based on the helper key.
        This enables versioning and A/B testing of helper implementations.

        Args:
            input_data: The usecase input (can be used to select helper version)

        Returns:
            The configured USECASE_CancelOrder instance

        Raises:
            RuntimeError: If the helper is not found in the registry
        """
        helper_key = "CONTRACT_HELPER_CancelOrder_V0"
        usecase_helper = self.helpers.get(helper_key)

        if usecase_helper is None:
            raise RuntimeError(f"Helper not found: {helper_key}")

        return USECASE_CancelOrder(usecase_helper, self.logger)
