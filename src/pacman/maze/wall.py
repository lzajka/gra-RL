from .maze_object import MazeObject
from src.pacman.game_config import GameConfig


class Wall(MazeObject):
    """Reprezentuje ścianę w labiryncie Pacmana.
    Ściana jest obiektem statycznym, który nie zmienia swojej pozycji ani stanu w trakcie gry.
    """

    def __init__(self, position: tuple[int, int]):
        """Inicjalizuje obiekt ściany na podstawie jego pozycji.

        :param position: Pozycja ściany w labiryncie w postaci krotki (x, y).
        :type position: tuple[int, int]
        """
        super().__init__(position)
        from src.pacman.maze import Maze
    
    def _draw(self):
        """Metoda zwracająca reprezentację obiektu w formie graficznej."""
        
        pass

    def to_csv_line():
        return []
    def get_csv_header():
        return []
    
    def _get_color(self):
        return GameConfig.WALL_COLOR
    
    def _get_filled_ratio(self):
        return GameConfig.WALL_FILLED_RATIO
    
    def _get_named_layer(self):
        return 'map'
    
    def copy(self):
        s = Wall(self.position)
        return s


MazeObject.character_to_class_mapping['#'] = Wall