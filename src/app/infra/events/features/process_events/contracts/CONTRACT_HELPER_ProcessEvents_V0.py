import importlib
from src.app.infra.events.features.process_events.interfaces.INTERFACE_HELPER_ProcessEvents import (
    INTERFACE_HELPER_ProcessEvents,
)
from src.app.infra.events.entities.event import Event
from src.app.infra.events.entities.abstract_event_processor import (
    AbstractEventProcessor,
)


class CONTRACT_HELPER_ProcessEvents_V0(INTERFACE_HELPER_ProcessEvents):

    def detect_event_processor(self, event: Event) -> AbstractEventProcessor:
        """
        Dynamically loads and returns an event processor based on the event name.

        Expected module path: src.app.infra.events.features.process_events.entities.concrete.<event_name>
        Expected class name: EventProcessor_<event_name>
        """
        module_path = f"src.app.infra.events.entities.concrete.{event.name}"
        class_name = f"EventProcessor_{event.name}"

        module = importlib.import_module(module_path)
        processor_class = getattr(module, class_name)
        return processor_class()
