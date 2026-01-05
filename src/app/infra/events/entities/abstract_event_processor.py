from abc import ABC, abstractmethod
from src.app.infra.events.entities.event import Event
from src.app.core.origin.schemas.ServiceOutput import ServiceOutput


class AbstractEventProcessor(ABC):

    @abstractmethod
    async def process(self, event: Event) -> ServiceOutput:
        pass
