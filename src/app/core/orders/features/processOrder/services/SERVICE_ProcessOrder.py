from src.app.core.orders.features.processOrder.contracts.CONTRACT_HELPER_ProcessOrder_V0 import (
    CONTRACT_HELPER_ProcessOrder_V0,
)
from src.app.core.orders.features.processOrder.usecases.USECASE_ProcessOrder import (
    USECASE_ProcessOrder,
)
from src.app.core.orders.features.processOrder.schemas.INPUT_ProcessOrder import (
    INPUT_ProcessOrder,
)
from src.app.core.orders.features.processOrder.schemas.OUTPUT_ProcessOrder import (
    OUTPUT_ProcessOrder,
)
from src.app.infra.logger.services.service_logger import get_service_logger


async def SERVICE_ProcessOrder(
    process_order_request: INPUT_ProcessOrder,
) -> OUTPUT_ProcessOrder:
    usecase_helper = CONTRACT_HELPER_ProcessOrder_V0()
    logger = get_service_logger()
    usecase = USECASE_ProcessOrder(usecase_helper, logger)
    return await usecase.execute(process_order_request)
