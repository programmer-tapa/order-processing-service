"""
Output schema for CancelOrder feature.

Contains the results of order cancellation including refund information.
"""

from typing import Optional
from src.app.core.orders.entities.Order import Order
from src.app.core.origin.entities.base_class import BaseClass


class OUTPUT_CancelOrder(BaseClass):
    """
    Output schema containing order cancellation results.

    Attributes:
        order: The cancelled order with updated status
        refund_amount: Amount to be refunded to customer
        message: Human-readable cancellation result message
        success: Whether cancellation completed successfully
    """

    order: Optional[Order] = None
    refund_amount: float = 0.0
    message: str = ""
    success: bool = False
