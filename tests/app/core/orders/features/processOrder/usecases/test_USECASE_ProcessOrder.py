"""
Tests for USECASE_ProcessOrder.

Tests the order processing workflow including validation, shipping calculation,
discount application, status updates, and customer notifications.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from src.app.core.orders.features.processOrder.usecases.USECASE_ProcessOrder import (
    USECASE_ProcessOrder,
)
from src.app.core.orders.features.processOrder.schemas.INPUT_ProcessOrder import (
    INPUT_ProcessOrder,
)
from src.app.core.orders.features.processOrder.schemas.OUTPUT_ProcessOrder import (
    OUTPUT_ProcessOrder,
)
from src.app.core.orders.features.processOrder.exceptions.OrderNotFoundException import (
    OrderNotFoundException,
)
from src.app.core.orders.features.processOrder.exceptions.InvalidOrderException import (
    InvalidOrderException,
)
from src.app.core.origin.schemas.ServiceStatus import ServiceStatus
from src.app.core.orders.entities.Order import Order


class TestUSECASE_ProcessOrder:

    @pytest.fixture
    def mock_order(self):
        """A valid order in 'new' status."""
        return Order(
            id=1,
            customer_name="Alice",
            total_amount=100.0,
            status="new",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
        )

    @pytest.fixture
    def mock_updated_order(self, mock_order):
        """Order with status updated to 'processing'."""
        return Order(
            id=mock_order.id,
            customer_name=mock_order.customer_name,
            total_amount=mock_order.total_amount,
            status="processing",
            created_at=mock_order.created_at,
            updated_at="2023-01-01T01:00:00Z",
        )

    @pytest.fixture
    def mock_logger(self):
        """Mock logger service."""
        logger = Mock()
        logger.info = Mock()
        logger.debug = Mock()
        logger.warning = Mock()
        logger.error = Mock()
        logger.critical = Mock()
        return logger

    @pytest.fixture
    def mock_helper(self, mock_order, mock_updated_order):
        """Mock helper with all required methods."""
        helper = Mock()
        helper.load_order = AsyncMock(return_value=mock_order)
        helper.validate_order = AsyncMock(return_value=None)
        helper.calculate_shipping = AsyncMock(return_value=5.99)
        helper.apply_discounts = AsyncMock(return_value=10.0)
        helper.update_order_status = AsyncMock(return_value=mock_updated_order)
        helper.notify_customer = AsyncMock(return_value=True)
        return helper

    @pytest.fixture
    def usecase(self, mock_helper, mock_logger):
        """Create usecase with mocked dependencies."""
        return USECASE_ProcessOrder(mock_helper, mock_logger)

    # ==================== Success Cases ====================

    @pytest.mark.asyncio
    async def test_execute_successfully_processes_order(
        self, usecase, mock_order, mock_updated_order
    ):
        """Test that execute successfully processes a valid order."""
        request = INPUT_ProcessOrder(order_id="1")

        result = await usecase.execute(request)

        assert result.success is True
        assert result.order == mock_updated_order
        assert result.shipping_cost == 5.99
        assert result.discount_applied == 10.0
        # final_total = 100.0 + 5.99 - 10.0 = 95.99
        assert result.final_total == 95.99
        assert "processed successfully" in result.message

    @pytest.mark.asyncio
    async def test_execute_returns_output_schema(self, usecase):
        """Test that execute returns an OUTPUT_ProcessOrder instance."""
        request = INPUT_ProcessOrder(order_id="1")

        result = await usecase.execute(request)

        assert isinstance(result, OUTPUT_ProcessOrder)

    @pytest.mark.asyncio
    async def test_execute_calls_load_order_with_correct_id(self, usecase, mock_helper):
        """Test that execute calls load_order with the correct order_id."""
        request = INPUT_ProcessOrder(order_id=42)

        await usecase.execute(request)

        mock_helper.load_order.assert_called_once_with(42)

    @pytest.mark.asyncio
    async def test_execute_calls_all_helper_methods_in_order(
        self, usecase, mock_helper, mock_order, mock_updated_order
    ):
        """Test that execute calls all helper methods in the correct order."""
        request = INPUT_ProcessOrder(order_id=1)

        await usecase.execute(request)

        # Verify all methods were called
        mock_helper.load_order.assert_called_once_with(1)
        mock_helper.validate_order.assert_called_once_with(mock_order)
        mock_helper.calculate_shipping.assert_called_once_with(mock_order)
        mock_helper.apply_discounts.assert_called_once_with(mock_order)
        mock_helper.update_order_status.assert_called_once_with(
            mock_order, "processing"
        )
        mock_helper.notify_customer.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_sends_correct_notification_message(
        self, usecase, mock_helper, mock_updated_order
    ):
        """Test that execute sends correct notification message to customer."""
        request = INPUT_ProcessOrder(order_id=1)

        await usecase.execute(request)

        # Verify notification was called with correct order and message format
        call_args = mock_helper.notify_customer.call_args
        assert call_args[0][0] == mock_updated_order
        notification_message = call_args[0][1]
        assert (
            "order #1" in notification_message.lower() or "#1" in notification_message
        )
        assert "95.99" in notification_message  # final total
        assert "5.99" in notification_message  # shipping

    # ==================== Exception Cases ====================

    @pytest.mark.asyncio
    async def test_execute_raises_order_not_found_exception(self, mock_logger):
        """Test that execute raises OrderNotFoundException when order is not found."""
        mock_helper = Mock()
        mock_helper.load_order = AsyncMock(
            side_effect=OrderNotFoundException("Order not found: 999")
        )
        usecase = USECASE_ProcessOrder(mock_helper, mock_logger)
        request = INPUT_ProcessOrder(order_id=999)

        with pytest.raises(OrderNotFoundException) as exc_info:
            await usecase.execute(request)

        assert "999" in str(exc_info.value)
        assert exc_info.value.status == ServiceStatus.NOT_FOUND

    @pytest.mark.asyncio
    async def test_execute_raises_invalid_order_exception(
        self, mock_order, mock_logger
    ):
        """Test that execute raises InvalidOrderException when order validation fails."""
        mock_helper = Mock()
        mock_helper.load_order = AsyncMock(return_value=mock_order)
        mock_helper.validate_order = AsyncMock(
            side_effect=InvalidOrderException(
                f"Order {mock_order.id} is not in a valid state for processing"
            )
        )
        usecase = USECASE_ProcessOrder(mock_helper, mock_logger)
        request = INPUT_ProcessOrder(order_id=1)

        with pytest.raises(InvalidOrderException) as exc_info:
            await usecase.execute(request)

        assert "not in a valid state" in str(exc_info.value)
        assert exc_info.value.status == ServiceStatus.VALIDATION_ERROR

    @pytest.mark.asyncio
    async def test_execute_does_not_continue_after_order_not_found(self, mock_logger):
        """Test that execute stops processing after OrderNotFoundException."""
        mock_helper = Mock()
        mock_helper.load_order = AsyncMock(
            side_effect=OrderNotFoundException("Order not found: 1")
        )
        mock_helper.validate_order = AsyncMock()
        mock_helper.calculate_shipping = AsyncMock()
        mock_helper.apply_discounts = AsyncMock()
        mock_helper.update_order_status = AsyncMock()
        mock_helper.notify_customer = AsyncMock()
        usecase = USECASE_ProcessOrder(mock_helper, mock_logger)
        request = INPUT_ProcessOrder(order_id="1")

        with pytest.raises(OrderNotFoundException):
            await usecase.execute(request)

        # These should NOT be called after exception
        mock_helper.validate_order.assert_not_called()
        mock_helper.calculate_shipping.assert_not_called()
        mock_helper.apply_discounts.assert_not_called()
        mock_helper.update_order_status.assert_not_called()
        mock_helper.notify_customer.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_does_not_continue_after_validation_failure(
        self, mock_order, mock_logger
    ):
        """Test that execute stops processing after InvalidOrderException."""
        mock_helper = Mock()
        mock_helper.load_order = AsyncMock(return_value=mock_order)
        mock_helper.validate_order = AsyncMock(
            side_effect=InvalidOrderException("Order is invalid")
        )
        mock_helper.calculate_shipping = AsyncMock()
        mock_helper.apply_discounts = AsyncMock()
        mock_helper.update_order_status = AsyncMock()
        mock_helper.notify_customer = AsyncMock()
        usecase = USECASE_ProcessOrder(mock_helper, mock_logger)
        request = INPUT_ProcessOrder(order_id="1")

        with pytest.raises(InvalidOrderException):
            await usecase.execute(request)

        # These should NOT be called after validation failure
        mock_helper.calculate_shipping.assert_not_called()
        mock_helper.apply_discounts.assert_not_called()
        mock_helper.update_order_status.assert_not_called()
        mock_helper.notify_customer.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_propagates_exception_from_helper(self, mock_logger):
        """Test that execute propagates exceptions from helper."""
        mock_helper = Mock()
        mock_helper.load_order = AsyncMock(side_effect=RuntimeError("Database error"))
        usecase = USECASE_ProcessOrder(mock_helper, mock_logger)
        request = INPUT_ProcessOrder(order_id="1")

        with pytest.raises(RuntimeError, match="Database error"):
            await usecase.execute(request)

    # ==================== Logging Tests ====================

    @pytest.mark.asyncio
    async def test_execute_logs_start_and_completion(self, usecase, mock_logger):
        """Test that execute logs start and completion messages."""
        request = INPUT_ProcessOrder(order_id="1")

        await usecase.execute(request)

        # Verify logger.info was called multiple times
        assert mock_logger.info.call_count >= 6
        # Check for start and completion logging
        log_messages = [str(call) for call in mock_logger.info.call_args_list]
        log_text = " ".join(log_messages)
        assert "Starting order processing" in log_text or "order_id" in log_text.lower()

    # ==================== Edge Cases ====================

    @pytest.mark.asyncio
    async def test_execute_handles_zero_shipping_cost(self, mock_logger):
        """Test that execute handles zero shipping cost correctly."""
        mock_order = Order(
            id=1,
            customer_name="Alice",
            total_amount=200.0,  # High amount for free shipping
            status="new",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
        )
        mock_updated_order = Order(
            id=1,
            customer_name="Alice",
            total_amount=200.0,
            status="processing",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T01:00:00Z",
        )
        mock_helper = Mock()
        mock_helper.load_order = AsyncMock(return_value=mock_order)
        mock_helper.validate_order = AsyncMock(return_value=None)
        mock_helper.calculate_shipping = AsyncMock(return_value=0.0)  # Free shipping
        mock_helper.apply_discounts = AsyncMock(return_value=20.0)
        mock_helper.update_order_status = AsyncMock(return_value=mock_updated_order)
        mock_helper.notify_customer = AsyncMock(return_value=True)
        usecase = USECASE_ProcessOrder(mock_helper, mock_logger)
        request = INPUT_ProcessOrder(order_id="1")

        result = await usecase.execute(request)

        assert result.success is True
        assert result.shipping_cost == 0.0
        # final_total = 200.0 + 0.0 - 20.0 = 180.0
        assert result.final_total == 180.0

    @pytest.mark.asyncio
    async def test_execute_handles_zero_discount(self, mock_logger):
        """Test that execute handles zero discount correctly."""
        mock_order = Order(
            id=1,
            customer_name="Alice",
            total_amount=50.0,
            status="new",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
        )
        mock_updated_order = Order(
            id=1,
            customer_name="Alice",
            total_amount=50.0,
            status="processing",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T01:00:00Z",
        )
        mock_helper = Mock()
        mock_helper.load_order = AsyncMock(return_value=mock_order)
        mock_helper.validate_order = AsyncMock(return_value=None)
        mock_helper.calculate_shipping = AsyncMock(return_value=5.99)
        mock_helper.apply_discounts = AsyncMock(return_value=0.0)  # No discount
        mock_helper.update_order_status = AsyncMock(return_value=mock_updated_order)
        mock_helper.notify_customer = AsyncMock(return_value=True)
        usecase = USECASE_ProcessOrder(mock_helper, mock_logger)
        request = INPUT_ProcessOrder(order_id="1")

        result = await usecase.execute(request)

        assert result.success is True
        assert result.discount_applied == 0.0
        # final_total = 50.0 + 5.99 - 0.0 = 55.99
        assert result.final_total == 55.99
