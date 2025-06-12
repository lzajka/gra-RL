from . import Ghost
from src.pacman.maze import Maze

class Inky(Ghost):
    """Reprezentuje ducha Inky w grze Pacman.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "Inky"
        Maze.get_main_instance().inky = self
        self.scatter_pos = Maze.get_main_instance().get_wall_near_corner("bottom-right")

    def get_scatter_position(self):
        """Zwraca pozycję scatter dla ducha Inky."""
        return self.scatter_pos
        

    def get_chase_position(self):
        """Zwraca pozycję chase dla ducha Inky."""
        return (1, 1)  # Przykładowa pozycja chase
    
    def copy(self):
        """Tworzy kopię ducha Inky."""
        return None
    
    @classmethod
    def get_instance(cls):
        """Zwraca instancję Inky'ego.
        
        :return: Instancja Inky'ego.
        :rtype: Inky
        """
        from src.pacman.maze import Maze
        return Maze.get_main_instance().inky