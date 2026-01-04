"""
Use case for processing orders.

Orchestrates the complete order processing workflow including
validation, shipping calculation, discounts, status updates,
and customer notifications.
"""

from src.app.core.orders.features.processOrder.interfaces.INTERFACE_HELPER_ProcessOrder import (
    INTERFACE_HELPER_ProcessOrder,
)
from src.app.core.origin.entities.abstract_usecase import AbstractUsecase
from src.app.core.orders.features.processOrder.schemas.INPUT_ProcessOrder import (
    INPUT_ProcessOrder,
)
from src.app.core.orders.features.processOrder.schemas.OUTPUT_ProcessOrder import (
    OUTPUT_ProcessOrder,
)
from src.app.infra.logger.interfaces.logger_service import LoggerService


class USECASE_ProcessOrder(AbstractUsecase):
    """
    Use case that processes an order through the complete workflow.

    Processing steps:
    1. Load order by ID
    2. Validate order is in processable state
    3. Calculate shipping cost
    4. Apply available discounts
    5. Calculate final total
    6. Update order status to 'processing'
    7. Notify customer of order processing
    """

    def __init__(
        self, usecase_helper: INTERFACE_HELPER_ProcessOrder, logger: LoggerService
    ):
        self._helper = usecase_helper
        self._logger = logger

    async def execute(self, input: INPUT_ProcessOrder) -> OUTPUT_ProcessOrder:
        """
        Execute the order processing workflow.

        Args:
            input: Contains the order_id to process

        Returns:
            OUTPUT_ProcessOrder with processing results
        """
        self._logger.info(f"{'='*60}")
        self._logger.info(
            f"[USECASE] Starting order processing for order ID: {input.order_id}"
        )
        self._logger.info(f"{'='*60}")

        # Step 1: Load the order
        order = await self._helper.load_order(input.order_id)

        if order is None:
            return OUTPUT_ProcessOrder(
                success=False,
                message=f"Order not found: {input.order_id}",
            )

        # Step 2: Validate the order
        is_valid = await self._helper.validate_order(order)

        if not is_valid:
            return OUTPUT_ProcessOrder(
                order=order,
                success=False,
                message=f"Order {order.id} is not in a valid state for processing (status: {order.status})",
            )

        # Step 3: Calculate shipping
        shipping_cost = await self._helper.calculate_shipping(order)

        # Step 4: Apply discounts
        discount = await self._helper.apply_discounts(order)

        # Step 5: Calculate final total
        final_total = order.total_amount + shipping_cost - discount
        self._logger.info(f"[USECASE] Order Summary:")
        self._logger.info(f"  Subtotal:  ${order.total_amount:.2f}")
        self._logger.info(f"  Shipping:  ${shipping_cost:.2f}")
        self._logger.info(f"  Discount: -${discount:.2f}")
        self._logger.info(f"  ─────────────────")
        self._logger.info(f"  Total:     ${final_total:.2f}")

        # Step 6: Update order status
        updated_order = await self._helper.update_order_status(order, "processing")

        # Step 7: Notify customer
        notification_message = (
            f"Your order #{order.id} is now being processed. "
            f"Total: ${final_total:.2f} (includes ${shipping_cost:.2f} shipping)"
        )
        await self._helper.notify_customer(updated_order, notification_message)

        self._logger.info(f"{'='*60}")
        self._logger.info(f"[USECASE] Order processing completed successfully!")
        self._logger.info(f"{'='*60}")

        return OUTPUT_ProcessOrder(
            order=updated_order,
            shipping_cost=shipping_cost,
            discount_applied=discount,
            final_total=final_total,
            message=f"Order {order.id} processed successfully for {order.customer_name}",
            success=True,
        )
