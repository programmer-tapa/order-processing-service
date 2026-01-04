from src.app.infra.event_processors.features.process_events.contracts.CONTRACT_HELPER_ProcessEvents_V0 import CONTRACT_HELPER_ProcessEvents_V0
from src.app.infra.event_processors.features.process_events.usecases.USECASE_ProcessEvents import USECASE_ProcessEvents
from src.app.infra.event_processors.features.process_events.schemas.INPUT_ProcessEvents import INPUT_ProcessEvents
from src.app.infra.event_processors.features.process_events.schemas.OUTPUT_ProcessEvents import OUTPUT_ProcessEvents


async def SERVICE_ProcessEvents(request: INPUT_ProcessEvents) -> OUTPUT_ProcessEvents:
    usecase_helper = CONTRACT_HELPER_ProcessEvents_V0()
    usecase = USECASE_ProcessEvents(usecase_helper)
    return await usecase.execute(request)
