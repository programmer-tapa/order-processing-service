from abc import ABC, abstractmethod
from typing import List
from src.app.core.orders.entities.Order import Order


class INTERFACE_HELPER_ProcessOrder(ABC):
    
    @abstractmethod
    async def load_order(self, order_id: int) -> List[Order]:
        pass
