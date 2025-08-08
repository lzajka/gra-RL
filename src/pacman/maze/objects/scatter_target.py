from .wall import Wall
from src.general.maze import  MazeObject
from typing import Tuple


scatter_targets = {}

class ScatterTarget(Wall):
    """Reprezentacja punktu scatter w labiryncie Pacmana.
    Zachowuje się identycznie do ściany, z tą różnicą, że zapisuje pozycje punktu.
    """
    name = None
    def __init__(self, position: tuple[int, int], parent):
        """Inicjalizuje obiekt na podstawie jego pozycji.

        :param position: Pozycja w labiryncie w postaci krotki (x, y).
        :type position: tuple[int, int]
        """
        global scatter_targets
        if self.name is None:
            raise ValueError("Nie nadano nazwy ducha dla ScatterTarget. Użyj klasy uzyskanej poprzez funkcję create_scatter_target")
        super().__init__(position, parent)
        scatter_targets[self.name] = self.position
        
    @classmethod
    def get_scatter_target(cls, ghost_name : str) -> Tuple[int, int]:
        """Zwraca pozycję punktu scatter dla danego ducha.

        :param ghost_name: Nazwa ducha, dla którego chcemy uzyskać pozycję punktu scatter.
        :type ghost_name: str
        :return: Pozycja punktu scatter w postaci krotki (x, y).
        :rtype: Tuple[int, int]
        """
        return scatter_targets.get(ghost_name, None)


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