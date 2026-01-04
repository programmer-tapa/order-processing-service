"""
Output schema for ProcessOrder feature.

Contains the results of order processing including calculated
shipping, discounts, and final totals.
"""

from typing import Optional
from src.app.core.orders.entities.Order import Order
from src.app.core.origin.entities.base_class import BaseClass


class OUTPUT_ProcessOrder(BaseClass):
    """
    Output schema containing order processing results.

    Attributes:
        order: The processed order with updated status
        shipping_cost: Calculated shipping cost
        discount_applied: Discount amount applied
        final_total: Final order total (order amount + shipping - discount)
        message: Human-readable processing result message
        success: Whether processing completed successfully
    """

    order: Optional[Order] = None
    shipping_cost: float = 0.0
    discount_applied: float = 0.0
    final_total: float = 0.0
    message: str = ""
    success: bool = False
