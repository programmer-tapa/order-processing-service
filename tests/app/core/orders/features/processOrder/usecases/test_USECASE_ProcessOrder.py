import pytest
from unittest.mock import Mock, AsyncMock
from src.app.core.orders.features.processOrder.usecases.USECASE_ProcessOrder import USECASE_ProcessOrder
from src.app.core.orders.features.processOrder.schemas.INPUT_ProcessOrder import INPUT_ProcessOrder
from src.app.core.orders.features.processOrder.schemas.OUTPUT_ProcessOrder import OUTPUT_ProcessOrder
from src.app.core.orders.entities.Order import Order


class TestUSECASE_ProcessOrder:

    @pytest.fixture
    def mock_orders(self):
        return [
            Order(
                id=1,
                customer_name="Alice",
                total_amount=100.0,
                status="new",
                created_at="2023-01-01T00:00:00Z",
                updated_at="2023-01-01T00:00:00Z"
            ),
            Order(
                id=2,
                customer_name="Bob",
                total_amount=200.0,
                status="processing",
                created_at="2023-01-01T00:00:00Z",
                updated_at="2023-01-01T00:00:00Z"
            )
        ]

    @pytest.fixture
    def mock_helper(self, mock_orders):
        helper = Mock()
        helper.load_order = AsyncMock(return_value=mock_orders)
        return helper

    @pytest.fixture
    def usecase(self, mock_helper):
        return USECASE_ProcessOrder(mock_helper)

    @pytest.mark.asyncio
    async def test_execute_returns_processed_orders(self, usecase, mock_orders):
        """Test that execute returns processed orders"""
        request = INPUT_ProcessOrder(order_id=1)

        result = await usecase.execute(request)

        assert result.processed_orders == mock_orders

    @pytest.mark.asyncio
    async def test_execute_calls_load_order_with_correct_id(self, usecase, mock_helper):
        """Test that execute calls load_order with the correct order_id"""
        request = INPUT_ProcessOrder(order_id=42)

        await usecase.execute(request)

        mock_helper.load_order.assert_called_once_with(42)

    @pytest.mark.asyncio
    async def test_execute_returns_output_schema(self, usecase):
        """Test that execute returns an OUTPUT_ProcessOrder instance"""
        request = INPUT_ProcessOrder(order_id=1)

        result = await usecase.execute(request)

        assert isinstance(result, OUTPUT_ProcessOrder)

    @pytest.mark.asyncio
    async def test_execute_returns_empty_list_when_no_orders(self):
        """Test that execute handles empty order list"""
        mock_helper = Mock()
        mock_helper.load_order = AsyncMock(return_value=[])
        usecase = USECASE_ProcessOrder(mock_helper)
        request = INPUT_ProcessOrder(order_id=999)

        result = await usecase.execute(request)

        assert result.processed_orders == []

    @pytest.mark.asyncio
    async def test_execute_propagates_exception(self):
        """Test that execute propagates exceptions from helper"""
        mock_helper = Mock()
        mock_helper.load_order = AsyncMock(side_effect=RuntimeError("Database error"))
        usecase = USECASE_ProcessOrder(mock_helper)
        request = INPUT_ProcessOrder(order_id=1)

        with pytest.raises(RuntimeError, match="Database error"):
            await usecase.execute(request)
