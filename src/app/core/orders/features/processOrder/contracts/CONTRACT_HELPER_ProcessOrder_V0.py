from typing import List
from src.app.core.orders.entities.Order import Order
from src.app.core.orders.features.processOrder.interfaces.INTERFACE_HELPER_ProcessOrder import (
    INTERFACE_HELPER_ProcessOrder,
)


class CONTRACT_HELPER_ProcessOrder_V0(INTERFACE_HELPER_ProcessOrder):

    async def load_order(self, order_id: int) -> List[Order]:

        mock_orders = [
            Order(
                id="1",
                customer_name="Alice",
                total_amount=100.0,
                status="new",
                created_at="2023-01-01T00:00:00Z",
                updated_at="2023-01-01T00:00:00Z",
            ),
            Order(
                id="2",
                customer_name="Bob",
                total_amount=200.0,
                status="processing",
                created_at="2023-01-01T00:00:00Z",
                updated_at="2023-01-01T00:00:00Z",
            ),
            Order(
                id="3",
                customer_name="Charlie",
                total_amount=300.0,
                status="completed",
                created_at="2023-01-01T00:00:00Z",
                updated_at="2023-01-01T00:00:00Z",
            ),
        ]

        if order_id:
            return [ord for ord in mock_orders if ord.id == order_id]
        return mock_orders
