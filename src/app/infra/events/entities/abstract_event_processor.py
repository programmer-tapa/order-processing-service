from abc import ABC, abstractmethod
from src.app.infra.events.entities.event import Event


class AbstractEventProcessor(ABC):

    @abstractmethod
    async def process(self, event: Event) -> None:
        pass
