from typing import List
from src.app.core.orders.entities.Order import Order
from src.app.core.origin.entities.base_class import BaseClass


class OUTPUT_ProcessOrder(BaseClass):
    processed_orders: List[Order]
