from abc import ABC, abstractmethod
from src.app.infra.events.entities.Event import Event

class AbstractEventProcessor(ABC):

    @abstractmethod
    def process(self, data: Event) -> None:
        pass
