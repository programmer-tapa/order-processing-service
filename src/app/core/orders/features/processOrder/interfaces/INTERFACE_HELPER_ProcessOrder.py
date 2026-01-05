"""
Interface for ProcessOrder feature helper.

Defines the contract for order processing operations that concrete
implementations must fulfill. This enables dependency inversion and
makes the use case testable with mock implementations.
"""

from abc import ABC, abstractmethod
from src.app.core.orders.entities.Order import Order


class INTERFACE_HELPER_ProcessOrder(ABC):
    """
    Abstract interface for order processing helper.

    Concrete implementations (e.g., CONTRACT_HELPER_ProcessOrder_V0)
    provide the actual logic for database access, external API calls, etc.
    """

    @abstractmethod
    async def load_order(self, order_id: str) -> Order:
        """
        Load an order by its ID from the data source.

        Args:
            order_id: The unique identifier of the order

        Returns:
            The Order if found

        Raises:
            OrderNotFoundException: If order with given ID does not exist
        """
        pass

    @abstractmethod
    async def validate_order(self, order: Order) -> None:
        """
        Validate that an order is in a processable state.

        Args:
            order: The order to validate

        Raises:
            InvalidOrderException: If the order is not valid for processing
        """
        pass

    @abstractmethod
    async def calculate_shipping(self, order: Order) -> float:
        """
        Calculate shipping cost for the order.

        Args:
            order: The order to calculate shipping for

        Returns:
            The shipping cost amount
        """
        pass

    @abstractmethod
    async def apply_discounts(self, order: Order) -> float:
        """
        Apply any applicable discounts to the order.

        Args:
            order: The order to apply discounts to

        Returns:
            The discount amount applied
        """
        pass

    @abstractmethod
    async def update_order_status(self, order: Order, new_status: str) -> Order:
        """
        Update the status of an order.

        Args:
            order: The order to update
            new_status: The new status to set

        Returns:
            The updated Order with new status
        """
        pass

    @abstractmethod
    async def notify_customer(self, order: Order, message: str) -> bool:
        """
        Send a notification to the customer about their order.

        Args:
            order: The order related to the notification
            message: The notification message

        Returns:
            True if notification was sent successfully, False otherwise
        """
        pass
