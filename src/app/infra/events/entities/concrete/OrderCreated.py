from src.app.infra.events.entities.abstract_event_processor import (
    AbstractEventProcessor,
)
from src.app.infra.events.entities.event import Event
from src.app.core.orders.features.processOrder.services.SERVICE_ProcessOrder import (
    SERVICE_ProcessOrder,
)
from src.app.core.orders.features.processOrder.schemas.INPUT_ProcessOrder import (
    INPUT_ProcessOrder,
)


class EventProcessor_OrderCreated(AbstractEventProcessor):

    async def process(self, event: Event) -> None:
        input = INPUT_ProcessOrder(order_id=event.data.get("orderId"))
        print(
            f"Processing OrderCreated event for order ID: {event.data.get('orderId')}"
        )
        result = await SERVICE_ProcessOrder(input)
