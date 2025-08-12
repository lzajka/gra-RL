from abc import abstractmethod, ABC
from .maze_object import MazeObject

class Collidable(ABC):

    def on_enter(self, obj : MazeObject):
        pass

    def on_exit(self, obj : MazeObject):
        pass

    def on_continue(self, obj : MazeObject):
        pass
