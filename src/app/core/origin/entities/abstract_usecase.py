from abc import ABC, abstractmethod


class AbstractUsecase(ABC):
    """
    Abstract base class for use cases.
    All use cases should inherit from this class and implement the execute method.
    """

    @abstractmethod
    def execute(self, *args, **kwargs):
        """
        Execute the use case logic.
        This method should be implemented by subclasses.
        """
        pass
