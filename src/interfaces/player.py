from abc import ABC, abstractmethod

class IPlayer(ABC):
    @abstractmethod
    def notify(self, state):
        pass

    @abstractmethod
    def play(self) -> int:
        pass