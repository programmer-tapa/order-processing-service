from src.app.infra.events.entities.abstract_event_processor import (
    AbstractEventProcessor,
)
from src.app.infra.events.entities.event import Event
from src.app.core.orders.features.processOrder.factory.FUNCTION_ProcessOrder import (
    FUNCTION_ProcessOrder,
)
from src.app.core.orders.features.processOrder.schemas.INPUT_ProcessOrder import (
    INPUT_ProcessOrder,
)

from src.app.core.origin.schemas.ServiceOutput import ServiceOutput


class EventProcessor_OrderCreated(AbstractEventProcessor):

    async def process(self, event: Event) -> ServiceOutput:
        input = INPUT_ProcessOrder(order_id=event.data.get("orderId"))
        result = await FUNCTION_ProcessOrder(input)
        return result
