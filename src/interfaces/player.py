from abc import ABC, abstractmethod
from game_state import IGameState

class IPlayer(ABC):
    @abstractmethod
    def notify(self, state : IGameState):
        pass

    @abstractmethod
    def play(self) -> int:
        pass