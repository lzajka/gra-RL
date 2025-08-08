from abc import abstractmethod, ABC
from .maze_object import MazeObject

class Collidable(ABC):

    @abstractmethod
    def on_collision(self, obj : MazeObject):
        pass
