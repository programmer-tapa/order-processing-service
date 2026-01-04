from src.app.core.orders.features.processOrder.contracts.CONTRACT_HELPER_ProcessOrder_V0 import CONTRACT_HELPER_ProcessOrder_V0
from src.app.core.orders.features.processOrder.usecases.USECASE_ProcessOrder import USECASE_ProcessOrder
from src.app.core.orders.features.processOrder.schemas.INPUT_ProcessOrder import INPUT_ProcessOrder
from src.app.core.orders.features.processOrder.schemas.OUTPUT_ProcessOrder import OUTPUT_ProcessOrder

async def SERVICE_ProcessOrder(process_order_request: INPUT_ProcessOrder) -> OUTPUT_ProcessOrder:
    usecase_helper = CONTRACT_HELPER_ProcessOrder_V0()
    usecase = USECASE_ProcessOrder(usecase_helper)
    return await usecase.execute(process_order_request)
