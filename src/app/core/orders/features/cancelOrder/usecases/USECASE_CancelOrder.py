"""
Use case for cancelling orders.

Orchestrates the complete order cancellation workflow including
validation, refund calculation, status updates, and customer notifications.
"""

from src.app.core.orders.features.cancelOrder.interfaces.INTERFACE_HELPER_CancelOrder import (
    INTERFACE_HELPER_CancelOrder,
)
from src.app.core.origin.entities.abstract_usecase import AbstractUsecase
from src.app.core.orders.features.cancelOrder.schemas.INPUT_CancelOrder import (
    INPUT_CancelOrder,
)
from src.app.core.orders.features.cancelOrder.schemas.OUTPUT_CancelOrder import (
    OUTPUT_CancelOrder,
)
from src.app.infra.logger.interfaces.logger_service import LoggerService


class USECASE_CancelOrder(AbstractUsecase):
    """
    Use case that cancels an order through the complete workflow.

    Cancellation steps:
    1. Load order by ID (throws OrderNotFoundException if not found)
    2. Validate order is cancellable (throws OrderNotCancellableException if not)
    3. Calculate refund amount
    4. Update order status to 'cancelled'
    5. Notify customer of cancellation
    """

    def __init__(
        self, usecase_helper: INTERFACE_HELPER_CancelOrder, logger: LoggerService
    ):
        self._helper = usecase_helper
        self._logger = logger

    async def execute(self, input: INPUT_CancelOrder) -> OUTPUT_CancelOrder:
        """
        Execute the order cancellation workflow.

        Args:
            input: Contains the order_id to cancel and optional reason

        Returns:
            OUTPUT_CancelOrder with cancellation results

        Raises:
            OrderNotFoundException: If order is not found
            OrderNotCancellableException: If order cannot be cancelled
        """
        self._logger.info(f"{'='*60}")
        self._logger.info(
            f"[USECASE] Starting order cancellation for order ID: {input.order_id}"
        )
        if input.cancellation_reason:
            self._logger.info(f"[USECASE] Reason: {input.cancellation_reason}")
        self._logger.info(f"{'='*60}")

        # Step 1: Load the order (throws OrderNotFoundException if not found)
        order = await self._helper.load_order(input.order_id)

        # Step 2: Validate the order is cancellable
        await self._helper.validate_cancellable(order)

        # Step 3: Calculate refund
        refund_amount = await self._helper.calculate_refund(order)

        self._logger.info(f"[USECASE] Cancellation Summary:")
        self._logger.info(f"  Order Total:   ${order.total_amount:.2f}")
        self._logger.info(f"  Refund Amount: ${refund_amount:.2f}")
        self._logger.info(f"  ─────────────────")

        # Step 4: Update order status
        updated_order = await self._helper.update_order_status(order, "cancelled")

        # Step 5: Notify customer
        reason_text = (
            f" Reason: {input.cancellation_reason}" if input.cancellation_reason else ""
        )
        notification_message = (
            f"Your order #{order.id} has been cancelled.{reason_text} "
            f"Refund of ${refund_amount:.2f} will be processed within 5-7 business days."
        )
        await self._helper.notify_customer(updated_order, notification_message)

        self._logger.info(f"{'='*60}")
        self._logger.info(f"[USECASE] Order cancellation completed successfully!")
        self._logger.info(f"{'='*60}")

        return OUTPUT_CancelOrder(
            order=updated_order,
            refund_amount=refund_amount,
            message=f"Order {order.id} cancelled successfully. Refund: ${refund_amount:.2f}",
            success=True,
        )
