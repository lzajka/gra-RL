from .wall import Wall
from .maze_object import MazeObject
from .maze import Maze
from src.pacman.game_config import GameConfig


class ScatterTarget(Wall):
    """Reprezentacja punktu scatter w labiryncie Pacmana.
    Zachowuje się identycznie do ściany, z tą różnicą, że zapisuje pozycje punktu.
    """
    name = None
    def __init__(self, position: tuple[int, int]):
        """Inicjalizuje obiekt na podstawie jego pozycji.

        :param position: Pozycja w labiryncie w postaci krotki (x, y).
        :type position: tuple[int, int]
        """
        if self.name is None:
            raise ValueError("Nie nadano nazwy ducha dla ScatterTarget. Użyj klasy uzyskanej poprzez funkcję create_scatter_target")
        super().__init__(position)
        maze = Maze.get_main_instance()
        maze.set_scatter_position(self.name, position)

def create_scatter_target(ghost_name : str) -> Wall:
    """Metoda modyfikująca klasę w celu przypisania konkretnego ducha.

    :param ghost_name: Nazwa ducha, dla którego tworzony jest punkt scatter.
    :type ghost_name: str
    """

    return type(f'{ghost_name}_ScatterTarget', (ScatterTarget, ), {
        'name': ghost_name
    })

MazeObject.character_to_class_mapping['p'] = create_scatter_target('pinky')
MazeObject.character_to_class_mapping['b'] = create_scatter_target('blinky')
MazeObject.character_to_class_mapping['c'] = create_scatter_target('clyde')
MazeObject.character_to_class_mapping['i'] = create_scatter_target('inky')