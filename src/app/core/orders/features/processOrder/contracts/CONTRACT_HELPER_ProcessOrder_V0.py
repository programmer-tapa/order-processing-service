"""
Concrete implementation of INTERFACE_HELPER_ProcessOrder.

This V0 contract provides mock/dummy implementations for development
and testing purposes. In production, this would be replaced with
real database queries and external service integrations.
"""

from typing import Optional
from datetime import datetime
from src.app.core.orders.entities.Order import Order
from src.app.core.orders.features.processOrder.interfaces.INTERFACE_HELPER_ProcessOrder import (
    INTERFACE_HELPER_ProcessOrder,
)
from src.app.infra.logger.services.service_logger import get_service_logger


class CONTRACT_HELPER_ProcessOrder_V0(INTERFACE_HELPER_ProcessOrder):
    """
    V0 implementation with dummy data for order processing.

    This contract simulates real order processing operations using
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
                status="processing",
                created_at="2024-01-03T09:15:00Z",
                updated_at="2024-01-03T11:00:00Z",
            ),
        }
        # Shipping rates based on order total
        self._shipping_rates = {
            "standard": 5.99,
            "express": 12.99,
            "free_threshold": 100.00,
        }
        # Discount configuration
        self._discount_percentage = 0.10  # 10% discount

    async def load_order(self, order_id: str) -> Optional[Order]:
        """Load order from mock database by ID."""
        self._logger.info(f"[CONTRACT] Loading order with ID: {order_id}")
        order = self._mock_orders.get(order_id)
        if order:
            self._logger.info(
                f"[CONTRACT] Found order for customer: {order.customer_name}"
            )
        else:
            self._logger.info(f"[CONTRACT] Order not found: {order_id}")
        return order

    async def validate_order(self, order: Order) -> bool:
        """
        Validate order is in a processable state.

        Order is valid if:
        - Status is 'new' or 'pending'
        - Total amount is greater than 0
        """
        self._logger.info(f"[CONTRACT] Validating order {order.id}...")

        valid_statuses = ["new", "pending"]
        is_valid_status = order.status in valid_statuses
        is_valid_amount = order.total_amount > 0

        is_valid = is_valid_status and is_valid_amount

        if not is_valid_status:
            self._logger.info(
                f"[CONTRACT] Invalid status: {order.status} (expected: {valid_statuses})"
            )
        if not is_valid_amount:
            self._logger.info(f"[CONTRACT] Invalid amount: {order.total_amount}")

        self._logger.info(
            f"[CONTRACT] Order validation result: {'VALID' if is_valid else 'INVALID'}"
        )
        return is_valid

    async def calculate_shipping(self, order: Order) -> float:
        """
        Calculate shipping cost based on order total.

        - Free shipping for orders over $100
        - Standard rate otherwise
        """
        self._logger.info(f"[CONTRACT] Calculating shipping for order {order.id}...")

        if order.total_amount >= self._shipping_rates["free_threshold"]:
            shipping = 0.00
            self._logger.info(
                f"[CONTRACT] Free shipping applied (order total >= ${self._shipping_rates['free_threshold']})"
            )
        else:
            shipping = self._shipping_rates["standard"]
            self._logger.info(f"[CONTRACT] Standard shipping: ${shipping}")

        return shipping

    async def apply_discounts(self, order: Order) -> float:
        """
        Apply 10% discount to the order total.

        In a real implementation, this would check for promo codes,
        loyalty programs, seasonal sales, etc.
        """
        self._logger.info(f"[CONTRACT] Applying discounts to order {order.id}...")

        discount = order.total_amount * self._discount_percentage
        self._logger.info(
            f"[CONTRACT] Applied {self._discount_percentage * 100}% discount: -${discount:.2f}"
        )

        return discount

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
        Send notification to customer (simulated).

        In production, this would integrate with email, SMS, or push
        notification services.
        """
        self._logger.info(
            f"[CONTRACT] Sending notification to {order.customer_name}..."
        )
        self._logger.info(f"[CONTRACT] Message: {message}")

        # Simulate successful notification
        self._logger.info(
            f"[CONTRACT] ✓ Notification sent successfully to {order.customer_name}"
        )
        return True
