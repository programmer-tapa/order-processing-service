from abc import ABC, abstractmethod


class AbstractFactory(ABC):
    """
    Abstract base class for factories.
    All factories should inherit from this class and implement the create method.
    """

    @abstractmethod
    def create(self, *args, **kwargs):
        """
        Create an instance of the product.
        This method should be implemented by subclasses.
        """
        pass
