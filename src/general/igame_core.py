from abc import ABC, abstractmethod

class IGameCore(ABC):
    @abstractmethod
    def restart(self, config):
        pass

    @abstractmethod
    def make_move(self, move):
        pass

    @abstractmethod
    def quit(self):
        pass