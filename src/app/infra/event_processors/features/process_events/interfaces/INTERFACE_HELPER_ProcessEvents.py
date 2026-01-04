from abc import ABC, abstractmethod
from src.app.infra.event_processors.features.process_events.schemas.INPUT_ProcessEvents import INPUT_ProcessEvents
from src.app.infra.event_processors.features.process_events.schemas.OUTPUT_ProcessEvents import OUTPUT_ProcessEvents
from src.app.infra.events.entities.Event import Event
from src.app.infra.event_processors.entities.AbstractEventProcessor import AbstractEventProcessor

class INTERFACE_HELPER_ProcessEvents(ABC):

    @abstractmethod
    def get_event_processor(self, event: Event) -> AbstractEventProcessor:
        pass

