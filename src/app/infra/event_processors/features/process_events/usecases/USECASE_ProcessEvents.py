from src.app.infra.event_processors.features.process_events.interfaces.INTERFACE_HELPER_ProcessEvents import INTERFACE_HELPER_ProcessEvents
from src.app.core.origin.entities.abstract_usecase import AbstractUsecase
from src.app.infra.event_processors.features.process_events.schemas.INPUT_ProcessEvents import INPUT_ProcessEvents
from src.app.infra.event_processors.features.process_events.schemas.OUTPUT_ProcessEvents import OUTPUT_ProcessEvents
from src.app.infra.events.entities.Event import Event
from src.app.infra.event_processors.entities.AbstractEventProcessor import AbstractEventProcessor


class USECASE_ProcessEvents(AbstractUsecase):

    def __init__(self, usecase_helper: INTERFACE_HELPER_ProcessEvents):
        self.usecase_helper = usecase_helper

    async def execute(self, request: INPUT_ProcessEvents) -> OUTPUT_ProcessEvents:
        try:
            event: Event = request.event
            event_processor: AbstractEventProcessor = self.usecase_helper.get_event_processor(event)
            await event_processor.process(event)
            return OUTPUT_ProcessEvents(success=True, message=f"Event processed successfully: {event.name}")
        except Exception as e:
            return OUTPUT_ProcessEvents(success=False, message=f"Failed to process event: {event.name}. Error: {str(e)}")

