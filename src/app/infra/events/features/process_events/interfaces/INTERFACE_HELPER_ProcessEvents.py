from abc import ABC, abstractmethod
from src.app.infra.events.features.process_events.schemas.INPUT_ProcessEvents import (
    INPUT_ProcessEvents,
)
from src.app.infra.events.features.process_events.schemas.OUTPUT_ProcessEvents import (
    OUTPUT_ProcessEvents,
)
from src.app.infra.events.entities.event import Event
from src.app.infra.events.entities.abstract_event_processor import (
    AbstractEventProcessor,
)


class INTERFACE_HELPER_ProcessEvents(ABC):

    @abstractmethod
    async def detect_event_processor(self, event: Event) -> AbstractEventProcessor:
        pass
