from src.app.infra.events.features.process_events.interfaces.INTERFACE_HELPER_ProcessEvents import (
    INTERFACE_HELPER_ProcessEvents,
)
from src.app.core.origin.entities.abstract_usecase import AbstractUsecase
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
from src.app.infra.logger.interfaces.logger_service import LoggerService
from src.app.core.origin.schemas.ServiceOutput import ServiceOutput


class USECASE_ProcessEvents(AbstractUsecase):

    def __init__(
        self, usecase_helper: INTERFACE_HELPER_ProcessEvents, logger: LoggerService
    ):
        self._helper = usecase_helper
        self._logger = logger

    async def execute(self, request: INPUT_ProcessEvents) -> OUTPUT_ProcessEvents:
        try:
            event: Event = request.event
            event_processor: AbstractEventProcessor = (
                self._helper.detect_event_processor(event)
            )
            result: ServiceOutput = await event_processor.process(event)
            self._logger.info(result)

            if not result.success:
                raise Exception(result.message)

            return OUTPUT_ProcessEvents(
                success=True, message=f"Event processed successfully: {event.name}"
            )
        except Exception as e:
            return OUTPUT_ProcessEvents(
                success=False,
                message=f"Failed to process event: {event.name}. Error: {str(e)}",
            )
