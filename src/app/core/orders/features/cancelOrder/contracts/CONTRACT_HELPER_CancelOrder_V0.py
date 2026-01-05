"""
Concrete implementation of INTERFACE_HELPER_CancelOrder.

This V0 contract provides mock/dummy implementations for development
and testing purposes. In production, this would be replaced with
real database queries and external service integrations.
"""

from datetime import datetime
from src.app.core.orders.entities.Order import Order
from src.app.core.orders.features.cancelOrder.interfaces.INTERFACE_HELPER_CancelOrder import (
    INTERFACE_HELPER_CancelOrder,
)
from src.app.core.orders.features.processOrder.exceptions.OrderNotFoundException import (
    OrderNotFoundException,
)
from src.app.core.orders.features.cancelOrder.exceptions.OrderNotCancellableException import (
    OrderNotCancellableException,
)
from src.app.infra.logger.services.service_logger import get_service_logger


class CONTRACT_HELPER_CancelOrder_V0(INTERFACE_HELPER_CancelOrder):
    """
    V0 implementation with dummy data for order cancellation.

    This contract simulates real order cancellation operations using
    in-memory mock data. Replace with actual implementations for production.
    """

    def __init__(self):
        self._logger = get_service_logger()
        """Initialize with mock order database."""
        self._mock_orders = {
            "1": Order(
                id="1",
                customer_name="Alice Johnson",
                total_amount=150.00,
                status="new",
                created_at="2024-01-01T10:00:00Z",
                updated_at="2024-01-01T10:00:00Z",
            ),
            "2": Order(
                id="2",
                customer_name="Bob Smith",
                total_amount=299.99,
                status="pending",
                created_at="2024-01-02T14:30:00Z",
                updated_at="2024-01-02T14:30:00Z",
            ),
            "3": Order(
                id="3",
                customer_name="Charlie Brown",
                total_amount=75.50,
                status="shipped",
                created_at="2024-01-03T09:15:00Z",
                updated_at="2024-01-03T11:00:00Z",
            ),
            "4": Order(
                id="4",
                customer_name="Diana Prince",
                total_amount=500.00,
                status="processing",
                created_at="2024-01-04T08:00:00Z",
                updated_at="2024-01-04T09:00:00Z",
            ),
        }
        # Cancellation fee configuration
        self._cancellation_fee_percentage = 0.05  # 5% cancellation fee

    async def load_order(self, order_id: str) -> Order:
        """
        Load order from mock database by ID.

        Raises:
            OrderNotFoundException: If order with given ID does not exist
        """
        self._logger.info(f"[CONTRACT] Loading order with ID: {order_id}")
        order = self._mock_orders.get(order_id)
        if order:
            self._logger.info(
                f"[CONTRACT] Found order for customer: {order.customer_name}"
            )
            return order
        else:
            self._logger.info(f"[CONTRACT] Order not found: {order_id}")
            raise OrderNotFoundException(f"Order not found: {order_id}")

    async def validate_cancellable(self, order: Order) -> None:
        """
        Validate order can be cancelled.

        Order is cancellable if status is 'new', 'pending', or 'processing'.

        Raises:
            OrderNotCancellableException: If order cannot be cancelled
        """
        self._logger.info(f"[CONTRACT] Validating order {order.id} is cancellable...")

        cancellable_statuses = ["new", "pending", "processing"]
        non_cancellable_statuses = ["shipped", "delivered", "cancelled"]

        if order.status in non_cancellable_statuses:
            self._logger.info(
                f"[CONTRACT] Order {order.id} cannot be cancelled (status: {order.status})"
            )
            raise OrderNotCancellableException(
                f"Order {order.id} cannot be cancelled (status: {order.status})"
            )

        if order.status not in cancellable_statuses:
            self._logger.info(
                f"[CONTRACT] Order {order.id} has unknown status: {order.status}"
            )
            raise OrderNotCancellableException(
                f"Order {order.id} has invalid status for cancellation: {order.status}"
            )

        self._logger.info(f"[CONTRACT] Order {order.id} is cancellable")

    async def calculate_refund(self, order: Order) -> float:
        """
        Calculate refund amount with cancellation fee.

        Refund = order total - 5% cancellation fee
        """
        self._logger.info(f"[CONTRACT] Calculating refund for order {order.id}...")

        cancellation_fee = order.total_amount * self._cancellation_fee_percentage
        refund_amount = order.total_amount - cancellation_fee

        self._logger.info(f"[CONTRACT] Order total: ${order.total_amount:.2f}")
        self._logger.info(
            f"[CONTRACT] Cancellation fee ({self._cancellation_fee_percentage * 100}%): ${cancellation_fee:.2f}"
        )
        self._logger.info(f"[CONTRACT] Refund amount: ${refund_amount:.2f}")

        return refund_amount

    async def update_order_status(self, order: Order, new_status: str) -> Order:
        """
        Update order status and timestamp.

        Creates a new Order instance with updated status (immutable pattern).
        """
        self._logger.info(
            f"[CONTRACT] Updating order {order.id} status: {order.status} -> {new_status}"
        )

        updated_order = Order(
            id=order.id,
            customer_name=order.customer_name,
            total_amount=order.total_amount,
            status=new_status,
            created_at=order.created_at,
            updated_at=datetime.utcnow().isoformat() + "Z",
        )

        # Update mock database
        self._mock_orders[order.id] = updated_order
        self._logger.info(f"[CONTRACT] Order {order.id} status updated successfully")

        return updated_order

    async def notify_customer(self, order: Order, message: str) -> bool:
        """
        Send cancellation notification to customer (simulated).

        In production, this would integrate with email, SMS, or push
        notification services.
        """
        self._logger.info(
            f"[CONTRACT] Sending cancellation notification to {order.customer_name}..."
        )
        self._logger.info(f"[CONTRACT] Message: {message}")

        # Simulate successful notification
        self._logger.info(
            f"[CONTRACT] ✓ Cancellation notification sent successfully to {order.customer_name}"
        )
        return True
