"""
Interface for CancelOrder feature helper.

Defines the contract for order cancellation operations that concrete
implementations must fulfill. This enables dependency inversion and
makes the use case testable with mock implementations.
"""

from abc import ABC, abstractmethod
from src.app.core.orders.entities.Order import Order


class INTERFACE_HELPER_CancelOrder(ABC):
    """
    Abstract interface for order cancellation helper.

    Concrete implementations (e.g., CONTRACT_HELPER_CancelOrder_V0)
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
    async def validate_cancellable(self, order: Order) -> None:
        """
        Validate that an order can be cancelled.

        An order can be cancelled if:
        - Status is 'new', 'pending', or 'processing'
        - Status is NOT 'shipped', 'delivered', or 'cancelled'

        Args:
            order: The order to validate

        Raises:
            OrderNotCancellableException: If the order cannot be cancelled
        """
        pass

    @abstractmethod
    async def calculate_refund(self, order: Order) -> float:
        """
        Calculate the refund amount for cancellation.

        Args:
            order: The order to calculate refund for

        Returns:
            The refund amount (may include cancellation fees)
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
        Send a cancellation notification to the customer.

        Args:
            order: The order related to the notification
            message: The notification message

        Returns:
            True if notification was sent successfully, False otherwise
        """
        pass
