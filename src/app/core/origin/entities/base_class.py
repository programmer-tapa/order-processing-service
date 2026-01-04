"""
Base class module for all domain entities in the application.

This module provides a foundational Pydantic BaseClass that all entities should inherit from.
It includes automatic camelCase alias generation for JSON serialization/deserialization,
enabling seamless integration with JavaScript/TypeScript frontends that use camelCase
while maintaining Python's snake_case convention internally.

Example:
    class Order(BaseClass):
        order_id: str
        customer_name: str

    # Can parse both formats:
    Order(order_id="123", customer_name="John")      # snake_case
    Order(orderId="123", customerName="John")        # camelCase

    # Serializes to camelCase by default:
    order.model_dump(by_alias=True)  # {"orderId": "123", "customerName": "John"}
"""

from pydantic import BaseModel, ConfigDict
from typing import *


def to_camel(string: str) -> str:
    """
    Convert a snake_case string to camelCase.

    This function is used as an alias generator for Pydantic models,
    allowing automatic conversion of Python snake_case field names
    to camelCase for JSON serialization.

    Args:
        string: A snake_case formatted string (e.g., "order_id", "customer_name")

    Returns:
        The camelCase equivalent (e.g., "orderId", "customerName")

    Example:
        >>> to_camel("order_id")
        'orderId'
        >>> to_camel("customer_name")
        'customerName'
    """
    components = string.split("_")
    # Keep first component lowercase, capitalize subsequent components
    return components[0] + "".join(x.title() for x in components[1:])


class BaseClass(BaseModel):
    """
    Base class for all domain entities in the application.

    Inherits from Pydantic's BaseModel and provides:
    - Automatic camelCase alias generation for JSON serialization
    - Bidirectional parsing (accepts both snake_case and camelCase)
    - Type validation and serialization from Pydantic

    All domain entities (Order, Event, etc.) should inherit from this class
    to ensure consistent JSON handling across the application.

    Attributes:
        model_config: Pydantic configuration with alias generation settings
    """

    model_config = ConfigDict(
        # Automatically generate camelCase aliases for all fields
        alias_generator=to_camel,
        # Allow parsing input using either the field name (snake_case) or alias (camelCase)
        populate_by_name=True,
    )
