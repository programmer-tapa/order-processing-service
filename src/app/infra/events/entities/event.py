from typing import Any
from src.app.core.origin.entities.base_class import BaseClass


class Event(BaseClass):
    id: str
    name: str
    data: Any
