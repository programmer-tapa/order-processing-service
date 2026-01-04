from abc import ABC, abstractmethod


class LoggerService(ABC):

    @abstractmethod
    def debug(self, payload):
        pass

    @abstractmethod
    def info(self, payload):
        pass

    @abstractmethod
    def warning(self, payload):
        pass

    @abstractmethod
    def error(self, payload):
        pass

    @abstractmethod
    def critical(self, payload):
        pass
