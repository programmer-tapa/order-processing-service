"""
Concrete implementation of INTERFACE_HELPER_ProcessOrder.

This V0 contract provides mock/dummy implementations for development
and testing purposes. In production, this would be replaced with
real database queries and external service integrations.

SIMULATED FAILURE CASES:
- Order ID "fraud-001": Triggers fraud check failure (amount > $10,000)
- Order ID "region-001": Triggers unsupported shipping region
- Order ID "inventory-001": Triggers out-of-stock simulation
- Order with status "cancelled" or "shipped": Validation failure
"""

from datetime import datetime
from src.app.core.orders.entities.Order import Order
from src.app.core.orders.features.processOrder.interfaces.INTERFACE_HELPER_ProcessOrder import (
    INTERFACE_HELPER_ProcessOrder,
)
from src.app.core.orders.features.processOrder.exceptions.OrderNotFoundException import (
    OrderNotFoundException,
)
from src.app.core.orders.features.processOrder.exceptions.InvalidOrderException import (
    InvalidOrderException,
)
from src.app.infra.logger.services.service_logger import get_service_logger


class CONTRACT_HELPER_ProcessOrder_V0(INTERFACE_HELPER_ProcessOrder):
    """
    V0 implementation with dummy data for order processing.

    This contract simulates real order processing operations using
    in-memory mock data. Replace with actual implementations for production.

    Includes simulated failure scenarios for testing error paths.
    """

    # Configuration for simulated failure thresholds
    FRAUD_THRESHOLD_AMOUNT = 10000.00
    UNSUPPORTED_REGIONS = ["Antarctica", "Mars Colony"]

    def __init__(self):
        self._logger = get_service_logger()
        """Initialize with mock order database including edge cases."""
        self._mock_orders = {
            # Normal orders
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
            # Edge case: Fraud detection trigger (high-value order)
            "fraud-001": Order(
                id="fraud-001",
                customer_name="Suspicious Buyer",
                total_amount=15000.00,  # Above fraud threshold
                status="new",
                created_at="2024-01-04T08:00:00Z",
                updated_at="2024-01-04T08:00:00Z",
            ),
            # Edge case: Unsupported shipping region
            "region-001": Order(
                id="region-001",
                customer_name="Antarctic Researcher",
                total_amount=500.00,
                status="new",
                created_at="2024-01-05T12:00:00Z",
                updated_at="2024-01-05T12:00:00Z",
            ),
            # Edge case: Out of stock simulation
            "inventory-001": Order(
                id="inventory-001",
                customer_name="Unlucky Customer",
                total_amount=99.99,
                status="new",
                created_at="2024-01-06T14:00:00Z",
                updated_at="2024-01-06T14:00:00Z",
            ),
            # Edge case: Already cancelled order
            "cancelled-001": Order(
                id="cancelled-001",
                customer_name="Changed Mind",
                total_amount=200.00,
                status="cancelled",
                created_at="2024-01-07T10:00:00Z",
                updated_at="2024-01-07T11:00:00Z",
            ),
        }

        # Region mapping for shipping validation
        self._order_regions = {
            "region-001": "Antarctica",
            "1": "USA",
            "2": "Canada",
            "3": "UK",
        }

        # Inventory status (for simulation)
        self._inventory_status = {
            "inventory-001": False,  # Out of stock
        }

        # Shipping rates based on order total
        self._shipping_rates = {
            "standard": 5.99,
            "express": 12.99,
            "free_threshold": 100.00,
        }
        # Discount configuration
        self._discount_percentage = 0.10  # 10% discount

    async def load_order(self, order_id: str) -> Order:
        """
        Load order from mock database by ID.

        Raises:
            OrderNotFoundException: If order with given ID does not exist
        """
        self._logger.info(f"[orderId={order_id}] Loading order from database...")
        order = self._mock_orders.get(order_id)
        if order:
            self._logger.info(
                f"[orderId={order_id}] Found order: customer={order.customer_name}, "
                f"amount=${order.total_amount:.2f}, status={order.status}"
            )
            return order
        else:
            self._logger.warning(f"[orderId={order_id}] Order not found in database")
            raise OrderNotFoundException(f"Order not found: {order_id}")

    async def validate_order(self, order: Order) -> None:
        """
        Validate order is in a processable state with comprehensive checks.

        Validation rules:
        1. Status must be 'new' or 'pending'
        2. Total amount must be > 0 and < fraud threshold
        3. Inventory must be available
        4. Shipping region must be supported

        Raises:
            InvalidOrderException: If any validation fails
        """
        self._logger.info(f"[orderId={order.id}] Starting order validation...")

        # Check 1: Valid status
        valid_statuses = ["new", "pending"]
        if order.status not in valid_statuses:
            self._logger.error(
                f"[orderId={order.id}] REJECTED: Invalid status '{order.status}' "
                f"(expected: {valid_statuses})"
            )
            raise InvalidOrderException(
                f"Order {order.id} cannot be processed (status: {order.status})"
            )
        self._logger.info(f"[orderId={order.id}] ✓ Status check passed: {order.status}")

        # Check 2: Valid amount
        if order.total_amount <= 0:
            self._logger.error(
                f"[orderId={order.id}] REJECTED: Invalid amount ${order.total_amount:.2f}"
            )
            raise InvalidOrderException(
                f"Order {order.id} has invalid amount: {order.total_amount}"
            )
        self._logger.info(
            f"[orderId={order.id}] ✓ Amount check passed: ${order.total_amount:.2f}"
        )

        # Check 3: Fraud detection (high-value orders)
        if order.total_amount > self.FRAUD_THRESHOLD_AMOUNT:
            self._logger.error(
                f"[orderId={order.id}] REJECTED: Fraud threshold exceeded "
                f"(${order.total_amount:.2f} > ${self.FRAUD_THRESHOLD_AMOUNT:.2f})"
            )
            raise InvalidOrderException(
                f"Order {order.id} flagged for fraud review: amount ${order.total_amount:.2f} "
                f"exceeds threshold ${self.FRAUD_THRESHOLD_AMOUNT:.2f}"
            )
        self._logger.info(f"[orderId={order.id}] ✓ Fraud check passed")

        # Check 4: Inventory availability
        if self._inventory_status.get(order.id) is False:
            self._logger.error(f"[orderId={order.id}] REJECTED: Items out of stock")
            raise InvalidOrderException(
                f"Order {order.id} cannot be fulfilled: items out of stock"
            )
        self._logger.info(f"[orderId={order.id}] ✓ Inventory check passed")

        self._logger.info(
            f"[orderId={order.id}] ✓ All validations passed - order is VALID"
        )

    async def calculate_shipping(self, order: Order) -> float:
        """
        Calculate shipping cost based on order total and region.

        - Free shipping for orders over $100
        - Standard rate otherwise
        - Rejects unsupported shipping regions

        Raises:
            InvalidOrderException: If shipping region is not supported
        """
        self._logger.info(f"[orderId={order.id}] Calculating shipping cost...")

        # Check shipping region
        region = self._order_regions.get(order.id, "USA")  # Default to USA
        if region in self.UNSUPPORTED_REGIONS:
            self._logger.error(
                f"[orderId={order.id}] REJECTED: Unsupported shipping region '{region}'"
            )
            raise InvalidOrderException(
                f"Order {order.id} cannot be shipped to {region}: region not supported"
            )
        self._logger.info(f"[orderId={order.id}] Shipping region: {region}")

        # Calculate shipping cost
        if order.total_amount >= self._shipping_rates["free_threshold"]:
            shipping = 0.00
            self._logger.info(
                f"[orderId={order.id}] Free shipping applied "
                f"(order >= ${self._shipping_rates['free_threshold']})"
            )
        else:
            shipping = self._shipping_rates["standard"]
            self._logger.info(
                f"[orderId={order.id}] Standard shipping: ${shipping:.2f}"
            )

        return shipping

    async def apply_discounts(self, order: Order) -> float:
        """
        Apply 10% discount to the order total.

        In a real implementation, this would check for promo codes,
        loyalty programs, seasonal sales, etc.
        """
        self._logger.info(f"[orderId={order.id}] Calculating discounts...")

        discount = order.total_amount * self._discount_percentage
        self._logger.info(
            f"[orderId={order.id}] Applied {self._discount_percentage * 100}% discount: "
            f"-${discount:.2f}"
        )

        return discount

    async def update_order_status(self, order: Order, new_status: str) -> Order:
        """
        Update order status and timestamp.

        Creates a new Order instance with updated status (immutable pattern).
        """
        self._logger.info(
            f"[orderId={order.id}] Updating status: {order.status} → {new_status}"
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
        self._logger.info(f"[orderId={order.id}] Status updated successfully")

        return updated_order

    async def notify_customer(self, order: Order, message: str) -> bool:
        """
        Send notification to customer (simulated).

        In production, this would integrate with email, SMS, or push
        notification services.
        """
        self._logger.info(
            f"[orderId={order.id}] Sending notification to {order.customer_name}..."
        )
        self._logger.info(f"[orderId={order.id}] Message: {message}")

        # Simulate successful notification
        self._logger.info(
            f"[orderId={order.id}] ✓ Notification sent to {order.customer_name}"
        )
        return True
