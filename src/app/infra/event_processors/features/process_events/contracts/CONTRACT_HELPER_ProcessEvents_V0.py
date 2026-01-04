import importlib
from src.app.infra.event_processors.features.process_events.interfaces.INTERFACE_HELPER_ProcessEvents import INTERFACE_HELPER_ProcessEvents
from src.app.infra.events.entities.Event import Event
from src.app.infra.event_processors.entities.AbstractEventProcessor import AbstractEventProcessor


class CONTRACT_HELPER_ProcessEvents_V0(INTERFACE_HELPER_ProcessEvents):

    def get_event_processor(self, event: Event) -> AbstractEventProcessor:
        module_path = f"src.app.infra.event_processors.features.process_events.entities.concrete.{event.name}"
        module = importlib.import_module(module_path)
        class_name = f"EventProcessor_{event.name}"
        processor_class = getattr(module, class_name)
        return processor_class()
