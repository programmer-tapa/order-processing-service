"""
Tests for CONTRACT_HELPER_ProcessOrder_V0 simulated failure scenarios.

These tests verify that the contract correctly handles edge cases
and failure scenarios including:
- Fraud detection (high-value orders)
- Unsupported shipping regions
- Out-of-stock inventory
- Invalid order status
"""

import pytest
from src.app.core.orders.features.processOrder.contracts.CONTRACT_HELPER_ProcessOrder_V0 import (
    CONTRACT_HELPER_ProcessOrder_V0,
)
from src.app.core.orders.features.processOrder.exceptions.OrderNotFoundException import (
    OrderNotFoundException,
)
from src.app.core.orders.features.processOrder.exceptions.InvalidOrderException import (
    InvalidOrderException,
)
from src.app.core.origin.schemas.ServiceStatus import ServiceStatus


class TestCONTRACT_SimulatedFailures:
    """Tests for simulated failure scenarios in the contract."""

    @pytest.fixture
    def contract(self):
        """Create a fresh contract instance for each test."""
        return CONTRACT_HELPER_ProcessOrder_V0()

    # ==================== Load Order Tests ====================

    @pytest.mark.asyncio
    async def test_load_order_success(self, contract):
        """Test loading a valid order."""
        order = await contract.load_order("1")

        assert order.id == "1"
        assert order.customer_name == "Alice Johnson"
        assert order.total_amount == 150.00

    @pytest.mark.asyncio
    async def test_load_order_not_found(self, contract):
        """Test loading a non-existent order raises OrderNotFoundException."""
        with pytest.raises(OrderNotFoundException) as exc_info:
            await contract.load_order("nonexistent-999")

        assert "nonexistent-999" in str(exc_info.value)
        assert exc_info.value.status == ServiceStatus.NOT_FOUND

    # ==================== Fraud Detection Tests ====================

    @pytest.mark.asyncio
    async def test_validate_order_fraud_threshold_exceeded(self, contract):
        """Test that high-value orders are rejected for fraud review."""
        fraud_order = await contract.load_order("fraud-001")

        with pytest.raises(InvalidOrderException) as exc_info:
            await contract.validate_order(fraud_order)

        assert "fraud review" in str(exc_info.value).lower()
        assert "15000" in str(exc_info.value)  # The order amount
        assert exc_info.value.status == ServiceStatus.VALIDATION_ERROR

    @pytest.mark.asyncio
    async def test_fraud_threshold_value(self, contract):
        """Test that fraud threshold is correctly configured."""
        assert contract.FRAUD_THRESHOLD_AMOUNT == 10000.00

    # ==================== Inventory Tests ====================

    @pytest.mark.asyncio
    async def test_validate_order_out_of_stock(self, contract):
        """Test that out-of-stock orders are rejected."""
        inventory_order = await contract.load_order("inventory-001")

        with pytest.raises(InvalidOrderException) as exc_info:
            await contract.validate_order(inventory_order)

        assert "out of stock" in str(exc_info.value).lower()
        assert exc_info.value.status == ServiceStatus.VALIDATION_ERROR

    # ==================== Shipping Region Tests ====================

    @pytest.mark.asyncio
    async def test_calculate_shipping_unsupported_region(self, contract):
        """Test that unsupported regions are rejected."""
        region_order = await contract.load_order("region-001")

        with pytest.raises(InvalidOrderException) as exc_info:
            await contract.calculate_shipping(region_order)

        assert "Antarctica" in str(exc_info.value)
        assert "not supported" in str(exc_info.value).lower()
        assert exc_info.value.status == ServiceStatus.VALIDATION_ERROR

    @pytest.mark.asyncio
    async def test_unsupported_regions_list(self, contract):
        """Test that unsupported regions are correctly configured."""
        assert "Antarctica" in contract.UNSUPPORTED_REGIONS
        assert "Mars Colony" in contract.UNSUPPORTED_REGIONS

    # ==================== Order Status Tests ====================

    @pytest.mark.asyncio
    async def test_validate_order_cancelled_status_rejected(self, contract):
        """Test that cancelled orders cannot be processed."""
        cancelled_order = await contract.load_order("cancelled-001")

        with pytest.raises(InvalidOrderException) as exc_info:
            await contract.validate_order(cancelled_order)

        assert "cancelled" in str(exc_info.value).lower()
        assert exc_info.value.status == ServiceStatus.VALIDATION_ERROR

    @pytest.mark.asyncio
    async def test_validate_order_processing_status_rejected(self, contract):
        """Test that orders already in 'processing' status are rejected."""
        # Order ID 3 has status "processing"
        processing_order = await contract.load_order("3")

        with pytest.raises(InvalidOrderException) as exc_info:
            await contract.validate_order(processing_order)

        assert "processing" in str(exc_info.value).lower()

    # ==================== Success Path Tests ====================

    @pytest.mark.asyncio
    async def test_validate_order_new_status_accepted(self, contract):
        """Test that 'new' status orders pass validation."""
        order = await contract.load_order("1")  # Status: new

        # Should not raise
        await contract.validate_order(order)

    @pytest.mark.asyncio
    async def test_validate_order_pending_status_accepted(self, contract):
        """Test that 'pending' status orders pass validation."""
        order = await contract.load_order("2")  # Status: pending

        # Should not raise
        await contract.validate_order(order)

    @pytest.mark.asyncio
    async def test_calculate_shipping_supported_region(self, contract):
        """Test shipping calculation for supported regions."""
        order = await contract.load_order("1")  # Region: USA

        shipping = await contract.calculate_shipping(order)

        # Order total is $150, which qualifies for free shipping ($100+ threshold)
        assert shipping == 0.00

    @pytest.mark.asyncio
    async def test_calculate_shipping_paid_shipping(self, contract):
        """Test shipping cost for orders below free threshold."""
        order = await contract.load_order("3")  # Total: $75.50 (below $100)

        shipping = await contract.calculate_shipping(order)

        assert shipping == 5.99  # Standard shipping rate

    # ==================== Edge Case Tests ====================

    @pytest.mark.asyncio
    async def test_full_workflow_success(self, contract):
        """Test complete order processing workflow for a valid order."""
        # Load
        order = await contract.load_order("1")

        # Validate
        await contract.validate_order(order)

        # Calculate shipping
        shipping = await contract.calculate_shipping(order)
        assert shipping == 0.00

        # Apply discounts
        discount = await contract.apply_discounts(order)
        assert discount == 15.00  # 10% of $150

        # Update status
        updated = await contract.update_order_status(order, "processing")
        assert updated.status == "processing"

        # Notify customer
        notified = await contract.notify_customer(updated, "Order processed!")
        assert notified is True

    @pytest.mark.asyncio
    async def test_mock_orders_contain_all_edge_cases(self, contract):
        """Test that all documented edge case orders exist."""
        # Verify all edge case orders are present
        assert "fraud-001" in contract._mock_orders
        assert "region-001" in contract._mock_orders
        assert "inventory-001" in contract._mock_orders
        assert "cancelled-001" in contract._mock_orders

        # Verify configurations
        assert (
            contract._mock_orders["fraud-001"].total_amount
            > contract.FRAUD_THRESHOLD_AMOUNT
        )
        assert contract._order_regions["region-001"] in contract.UNSUPPORTED_REGIONS
        assert contract._inventory_status["inventory-001"] is False
        assert contract._mock_orders["cancelled-001"].status == "cancelled"
