from src.app.core.origin.entities.base_class import BaseClass
from typing import Any
from src.app.infra.events.entities.Event import Event

class INPUT_ProcessEvents(BaseClass):
    event: Event
