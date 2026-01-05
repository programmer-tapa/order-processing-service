"""
Input schema for CancelOrder feature.

Contains the order ID and optional cancellation reason.
"""

from typing import Optional
from src.app.core.origin.entities.base_class import BaseClass


class INPUT_CancelOrder(BaseClass):
    """
    Input schema for order cancellation request.

    Attributes:
        order_id: The unique identifier of the order to cancel
        cancellation_reason: Optional reason for cancellation
    """

    order_id: str
    cancellation_reason: Optional[str] = None
