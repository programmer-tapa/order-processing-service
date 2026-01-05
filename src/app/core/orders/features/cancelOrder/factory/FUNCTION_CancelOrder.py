"""
Factory function for creating and running SERVICE_CancelOrder.

This module provides a simple factory approach (Approach 1) for dependency injection,
similar to Spring's @Bean pattern but without a framework.
"""

from typing import Optional

from src.app.core.orders.features.cancelOrder.contracts.CONTRACT_HELPER_CancelOrder_V0 import (
    CONTRACT_HELPER_CancelOrder_V0,
)
from src.app.core.orders.features.cancelOrder.interfaces.INTERFACE_HELPER_CancelOrder import (
    INTERFACE_HELPER_CancelOrder,
)
from src.app.core.orders.features.cancelOrder.schemas.INPUT_CancelOrder import (
    INPUT_CancelOrder,
)
from src.app.core.orders.features.cancelOrder.schemas.OUTPUT_CancelOrder import (
    OUTPUT_CancelOrder,
)
from src.app.core.orders.features.cancelOrder.services.SERVICE_CancelOrder import (
    SERVICE_CancelOrder,
)
from src.app.core.origin.interfaces.UsecaseAuthorizationService import (
    UsecaseAuthorizationService,
)
from src.app.core.origin.schemas.ServiceDependency import ServiceDependency
from src.app.core.origin.schemas.ServiceInput import ServiceInput
from src.app.core.origin.schemas.ServiceOutput import ServiceOutput
from src.app.core.origin.schemas.User import User


def create_cancel_order_service(
    authorization_service: Optional[UsecaseAuthorizationService] = None,
    helpers: Optional[dict[str, INTERFACE_HELPER_CancelOrder]] = None,
) -> SERVICE_CancelOrder:
    """
    Factory function to create a fully configured SERVICE_CancelOrder.

    Similar to Spring's @Bean - creates the service with all dependencies wired.

    Args:
        authorization_service: Optional authorization service for user authorization
        helpers: Optional custom helpers map. If None, uses default CONTRACT_HELPER_CancelOrder_V0

    Returns:
        A fully configured SERVICE_CancelOrder instance
    """
    dependencies = ServiceDependency(authorization_service=authorization_service)

    if helpers is None:
        helpers = {
            "CONTRACT_HELPER_CancelOrder_V0": CONTRACT_HELPER_CancelOrder_V0(),
        }

    return SERVICE_CancelOrder(dependencies=dependencies, helpers=helpers)


# Singleton instance (lazy initialization)
_service_instance: Optional[SERVICE_CancelOrder] = None


def get_cancel_order_service() -> SERVICE_CancelOrder:
    """
    Get the singleton SERVICE_CancelOrder instance.

    Uses lazy initialization - the service is created on first call.

    Returns:
        The singleton SERVICE_CancelOrder instance
    """
    global _service_instance
    if _service_instance is None:
        _service_instance = create_cancel_order_service()
    return _service_instance


async def FUNCTION_CancelOrder(
    input_data: INPUT_CancelOrder,
    user: Optional[User] = None,
) -> ServiceOutput[OUTPUT_CancelOrder]:
    """
    Cancel an order.

    This is the main entry point for cancelling orders. It:
    1. Creates (or reuses) the SERVICE_CancelOrder instance
    2. Wraps the input in ServiceInput with user context
    3. Runs the service and returns the structured ServiceOutput

    Args:
        input_data: The INPUT_CancelOrder containing order ID and optional reason
        user: Optional user context for authorization. If None, authorization
              will fail unless no authorization service is configured.

    Returns:
        ServiceOutput containing:
        - status: ServiceStatus indicating success/failure
        - data: OUTPUT_CancelOrder on success, None on failure
        - error_message: Error description on failure, None on success

    Example:
        # Without authorization
        input_data = INPUT_CancelOrder(order_id="123", cancellation_reason="Changed my mind")
        result = await FUNCTION_CancelOrder(input_data)

        # With authorization
        user = User(id="1", username="admin", roles=["admin"])
        input_data = INPUT_CancelOrder(order_id="123")
        result = await FUNCTION_CancelOrder(input_data, user=user)

        if result.status == ServiceStatus.SUCCESS:
            print(f"Order cancelled: {result.data}")
        else:
            print(f"Error: {result.error_message}")
    """
    service = get_cancel_order_service()

    service_input = ServiceInput(user=user, data=input_data)

    return await service.run(service_input)
