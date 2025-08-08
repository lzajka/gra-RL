from abc import abstractmethod
from .maze import Maze
class UsesMaze:
    """Klasa definiująca metodę, którą musi implementować GameCore aby wykorzystać Maze.
    """

    @classmethod
    def get_maze(cls) -> Maze:
        raise NotImplementedError("Metoda get_maze nie została zaimplementowana.")