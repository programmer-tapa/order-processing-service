"""
Tests for USECASE_CancelOrder.

Tests the order cancellation workflow including validation, refund calculation,
status updates, and customer notifications.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from src.app.core.orders.features.cancelOrder.usecases.USECASE_CancelOrder import (
    USECASE_CancelOrder,
)
from src.app.core.orders.features.cancelOrder.schemas.INPUT_CancelOrder import (
    INPUT_CancelOrder,
)
from src.app.core.orders.features.cancelOrder.schemas.OUTPUT_CancelOrder import (
    OUTPUT_CancelOrder,
)
from src.app.core.orders.features.processOrder.exceptions.OrderNotFoundException import (
    OrderNotFoundException,
)
from src.app.core.orders.features.cancelOrder.exceptions.OrderNotCancellableException import (
    OrderNotCancellableException,
)
from src.app.core.origin.schemas.ServiceStatus import ServiceStatus
from src.app.core.orders.entities.Order import Order


class TestUSECASE_CancelOrder:

    @pytest.fixture
    def mock_order(self):
        """A valid order in 'pending' status (cancellable)."""
        return Order(
            id="1",
            customer_name="Alice",
            total_amount=100.0,
            status="pending",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
        )

    @pytest.fixture
    def mock_cancelled_order(self, mock_order):
        """Order with status updated to 'cancelled'."""
        return Order(
            id=mock_order.id,
            customer_name=mock_order.customer_name,
            total_amount=mock_order.total_amount,
            status="cancelled",
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
    def mock_helper(self, mock_order, mock_cancelled_order):
        """Mock helper with all required methods."""
        helper = Mock()
        helper.load_order = AsyncMock(return_value=mock_order)
        helper.validate_cancellable = AsyncMock(return_value=None)
        helper.calculate_refund = AsyncMock(return_value=95.0)  # 5% fee
        helper.update_order_status = AsyncMock(return_value=mock_cancelled_order)
        helper.notify_customer = AsyncMock(return_value=True)
        return helper

    @pytest.fixture
    def usecase(self, mock_helper, mock_logger):
        """Create usecase with mocked dependencies."""
        return USECASE_CancelOrder(mock_helper, mock_logger)

    # ==================== Success Cases ====================

    @pytest.mark.asyncio
    async def test_execute_successfully_cancels_order(
        self, usecase, mock_order, mock_cancelled_order
    ):
        """Test that execute successfully cancels a valid order."""
        request = INPUT_CancelOrder(order_id="1")

        result = await usecase.execute(request)

        assert result.success is True
        assert result.order == mock_cancelled_order
        assert result.refund_amount == 95.0
        assert "cancelled successfully" in result.message

    @pytest.mark.asyncio
    async def test_execute_with_cancellation_reason(
        self, usecase, mock_order, mock_cancelled_order
    ):
        """Test cancellation with a reason."""
        request = INPUT_CancelOrder(order_id="1", cancellation_reason="Changed my mind")

        result = await usecase.execute(request)

        assert result.success is True
        assert result.order == mock_cancelled_order

    @pytest.mark.asyncio
    async def test_execute_returns_output_schema(self, usecase):
        """Test that execute returns an OUTPUT_CancelOrder instance."""
        request = INPUT_CancelOrder(order_id="1")

        result = await usecase.execute(request)

        assert isinstance(result, OUTPUT_CancelOrder)

    @pytest.mark.asyncio
    async def test_execute_calls_all_helper_methods_in_order(
        self, usecase, mock_helper, mock_order, mock_cancelled_order
    ):
        """Test that execute calls all helper methods in the correct order."""
        request = INPUT_CancelOrder(order_id="1")

        await usecase.execute(request)

        # Verify all methods were called
        mock_helper.load_order.assert_called_once_with("1")
        mock_helper.validate_cancellable.assert_called_once_with(mock_order)
        mock_helper.calculate_refund.assert_called_once_with(mock_order)
        mock_helper.update_order_status.assert_called_once_with(mock_order, "cancelled")
        mock_helper.notify_customer.assert_called_once()

    # ==================== Exception Cases ====================

    @pytest.mark.asyncio
    async def test_execute_raises_order_not_found_exception(self, mock_logger):
        """Test that execute raises OrderNotFoundException when order is not found."""
        mock_helper = Mock()
        mock_helper.load_order = AsyncMock(
            side_effect=OrderNotFoundException("Order not found: 999")
        )
        usecase = USECASE_CancelOrder(mock_helper, mock_logger)
        request = INPUT_CancelOrder(order_id="999")

        with pytest.raises(OrderNotFoundException) as exc_info:
            await usecase.execute(request)

        assert "999" in str(exc_info.value)
        assert exc_info.value.status == ServiceStatus.NOT_FOUND

    @pytest.mark.asyncio
    async def test_execute_raises_order_not_cancellable_exception(
        self, mock_order, mock_logger
    ):
        """Test that execute raises OrderNotCancellableException for shipped orders."""
        mock_helper = Mock()
        mock_helper.load_order = AsyncMock(return_value=mock_order)
        mock_helper.validate_cancellable = AsyncMock(
            side_effect=OrderNotCancellableException(
                f"Order {mock_order.id} cannot be cancelled (status: shipped)"
            )
        )
        usecase = USECASE_CancelOrder(mock_helper, mock_logger)
        request = INPUT_CancelOrder(order_id="1")

        with pytest.raises(OrderNotCancellableException) as exc_info:
            await usecase.execute(request)

        assert "cannot be cancelled" in str(exc_info.value)
        assert exc_info.value.status == ServiceStatus.VALIDATION_ERROR

    @pytest.mark.asyncio
    async def test_execute_does_not_continue_after_order_not_found(self, mock_logger):
        """Test that execute stops processing after OrderNotFoundException."""
        mock_helper = Mock()
        mock_helper.load_order = AsyncMock(
            side_effect=OrderNotFoundException("Order not found: 1")
        )
        mock_helper.validate_cancellable = AsyncMock()
        mock_helper.calculate_refund = AsyncMock()
        mock_helper.update_order_status = AsyncMock()
        mock_helper.notify_customer = AsyncMock()
        usecase = USECASE_CancelOrder(mock_helper, mock_logger)
        request = INPUT_CancelOrder(order_id="1")

        with pytest.raises(OrderNotFoundException):
            await usecase.execute(request)

        # These should NOT be called after exception
        mock_helper.validate_cancellable.assert_not_called()
        mock_helper.calculate_refund.assert_not_called()
        mock_helper.update_order_status.assert_not_called()
        mock_helper.notify_customer.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_does_not_continue_after_validation_failure(
        self, mock_order, mock_logger
    ):
        """Test that execute stops processing after OrderNotCancellableException."""
        mock_helper = Mock()
        mock_helper.load_order = AsyncMock(return_value=mock_order)
        mock_helper.validate_cancellable = AsyncMock(
            side_effect=OrderNotCancellableException("Order cannot be cancelled")
        )
        mock_helper.calculate_refund = AsyncMock()
        mock_helper.update_order_status = AsyncMock()
        mock_helper.notify_customer = AsyncMock()
        usecase = USECASE_CancelOrder(mock_helper, mock_logger)
        request = INPUT_CancelOrder(order_id="1")

        with pytest.raises(OrderNotCancellableException):
            await usecase.execute(request)

        # These should NOT be called after validation failure
        mock_helper.calculate_refund.assert_not_called()
        mock_helper.update_order_status.assert_not_called()
        mock_helper.notify_customer.assert_not_called()

    # ==================== Edge Cases ====================

    @pytest.mark.asyncio
    async def test_execute_handles_full_refund(self, mock_logger):
        """Test cancellation with full refund (no cancellation fee)."""
        mock_order = Order(
            id="1",
            customer_name="Alice",
            total_amount=100.0,
            status="new",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
        )
        mock_cancelled_order = Order(
            id="1",
            customer_name="Alice",
            total_amount=100.0,
            status="cancelled",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T01:00:00Z",
        )
        mock_helper = Mock()
        mock_helper.load_order = AsyncMock(return_value=mock_order)
        mock_helper.validate_cancellable = AsyncMock(return_value=None)
        mock_helper.calculate_refund = AsyncMock(return_value=100.0)  # Full refund
        mock_helper.update_order_status = AsyncMock(return_value=mock_cancelled_order)
        mock_helper.notify_customer = AsyncMock(return_value=True)
        usecase = USECASE_CancelOrder(mock_helper, mock_logger)
        request = INPUT_CancelOrder(order_id="1")

        result = await usecase.execute(request)

        assert result.success is True
        assert result.refund_amount == 100.0

    @pytest.mark.asyncio
    async def test_execute_logs_start_and_completion(self, usecase, mock_logger):
        """Test that execute logs start and completion messages."""
        request = INPUT_CancelOrder(order_id="1")

        await usecase.execute(request)

        # Verify logger.info was called multiple times
        assert mock_logger.info.call_count >= 6
        # Check for start and completion logging
        log_messages = [str(call) for call in mock_logger.info.call_args_list]
        log_text = " ".join(log_messages)
        assert (
            "Starting order cancellation" in log_text or "order_id" in log_text.lower()
        )
