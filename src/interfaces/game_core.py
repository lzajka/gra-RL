from abc import ABC, abstractmethod
from game_config import IGameConfig
from player_move import IPlayerMove

class IGameCore(ABC):
    @abstractmethod
    def restart(self, config : IGameConfig):
        pass

    @abstractmethod
    def make_move(self, move : IPlayerMove):
        pass

    @abstractmethod
    def quit(self):
        pass