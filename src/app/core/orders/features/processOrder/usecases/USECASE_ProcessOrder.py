from src.app.core.orders.features.processOrder.interfaces.INTERFACE_HELPER_ProcessOrder import INTERFACE_HELPER_ProcessOrder
from src.app.core.origin.entities.abstract_usecase import AbstractUsecase
from src.app.core.orders.features.processOrder.schemas.INPUT_ProcessOrder import INPUT_ProcessOrder
from src.app.core.orders.features.processOrder.schemas.OUTPUT_ProcessOrder import OUTPUT_ProcessOrder
import asyncio

class USECASE_ProcessOrder(AbstractUsecase):

    def __init__(self, usecase_helper: INTERFACE_HELPER_ProcessOrder):
        self.usecase_helper = usecase_helper

    async def execute(self, request: INPUT_ProcessOrder) -> OUTPUT_ProcessOrder:
        orders_task = self.usecase_helper.load_order(request.order_id)
        # Assuming we just reload orders for now, similar to load_category loading categories and products
        # If we had a second thing to load, we would gather it here.
        # For strict compliance with the reference which gathers two tasks:
        orders = await orders_task 
        return OUTPUT_ProcessOrder(processed_orders=orders)
