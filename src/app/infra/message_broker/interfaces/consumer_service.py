from abc import ABC, abstractmethod


class ConsumerService(ABC):

    @abstractmethod
    def _poll_wrapper(self):
        """Wrapper method for polling messages."""
        pass

    @abstractmethod
    def start_scheduler(self):
        """Start the scheduler in a separate thread."""
        pass

    @abstractmethod
    def stop_scheduler(self):
        """Stop the scheduler and cleanup resources."""
        pass
