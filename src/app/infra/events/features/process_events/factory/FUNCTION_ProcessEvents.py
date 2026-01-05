from src.app.infra.events.features.process_events.contracts.CONTRACT_HELPER_ProcessEvents_V0 import (
    CONTRACT_HELPER_ProcessEvents_V0,
)
from src.app.infra.events.features.process_events.usecases.USECASE_ProcessEvents import (
    USECASE_ProcessEvents,
)
from src.app.infra.events.features.process_events.schemas.INPUT_ProcessEvents import (
    INPUT_ProcessEvents,
)
from src.app.infra.events.features.process_events.schemas.OUTPUT_ProcessEvents import (
    OUTPUT_ProcessEvents,
)

from src.app.infra.logger.services.service_logger import get_service_logger


async def FUNCTION_ProcessEvents(request: INPUT_ProcessEvents) -> OUTPUT_ProcessEvents:
    usecase_helper = CONTRACT_HELPER_ProcessEvents_V0()
    logger = get_service_logger()
    usecase = USECASE_ProcessEvents(usecase_helper, logger)
    return await usecase.execute(request)
