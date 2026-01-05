"""
Container for service dependencies.

Mirrors the Java ServiceDependency record from order-service.
Encapsulates all common dependencies required by services.
"""

from dataclasses import dataclass, field
from typing import Optional

from src.app.core.origin.interfaces.UsecaseAuthorizationService import (
    UsecaseAuthorizationService,
)


@dataclass
class ServiceDependency:
    """
    Container for service dependencies.

    Encapsulates all common dependencies required by services.
    This allows adding new cross-cutting dependencies without
    changing service constructor signatures.

    Attributes:
        authorization_service: The service used for user authorization (optional)
    """

    authorization_service: Optional[UsecaseAuthorizationService] = field(default=None)

    # Future dependencies can be added here without breaking existing code:
    # logger: Optional[Logger] = field(default=None)
    # event_publisher: Optional[EventPublisher] = field(default=None)
    # metrics_service: Optional[MetricsService] = field(default=None)
