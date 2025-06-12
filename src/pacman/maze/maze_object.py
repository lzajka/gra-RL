from abc import ABC, abstractmethod
from typing import List
from . import Maze
from typing import Tuple
from src.general import Drawable


class MazeObject(Drawable):
    """Klasa abstrakcyjna reprezentująca obiekt znajdujący się w labiryncie.
    """
    character_to_class_mapping = {}
    def __init__(self, position: tuple[int, int]):
        """Inicjalizuje obiekt labiryntu na podstawie jego pozycji.

        :param position: Pozycja obiektu w labiryncie w postaci krotki (x, y).
        :type position: tuple[int, int]
        """
        self.maze = Maze.get_main_instance()
        self.position = position
        self.draw()
        
        self.maze._add_object(self)


    @abstractmethod
    def to_csv_line() -> List[str]:
        pass

    @abstractmethod
    def get_csv_header() -> List[str]:
        pass

    
    def get_position(self) -> tuple[int, int]:
        """Zwraca pozycję obiektu w labiryncie.

        :return: Pozycja obiektu w postaci krotki (x, y).
        :rtype: tuple[int, int]
        """
        return self.position

    def set_position(self, position: tuple[int, int]):
        """Ustawia pozycję obiektu w labiryncie.

        :param position: Nowa pozycja obiektu w postaci krotki (x, y).
        :type position: tuple[int, int]
        """
        self.erase()
        self.maze._remove_object(self)
        self.position = position
        self.draw()
        self.maze._add_object(self)

    def destroy(self):
        """Usuwa obiekt z labiryntu."""
        self.erase()
        self.maze._remove_object(self)


    def _on_update(self):
        """Metoda wywoływana podczas aktualizacji obiektu. Może być nadpisana w klasach dziedziczących."""
        pass

    def get_color(self):
        """Metoda zwracająca kolor obiektu. Może być nadpisana w klasach dziedziczących."""
        pass

    def _get_grid_cell_size(self):
        from src.pacman.game_core import GameCore
        return GameCore.get_main_instance().get_grid_cell_size()

    def _get_game_core(self):
        from src.pacman.game_core import GameCore
        return GameCore.get_main_instance()
    
    @abstractmethod
    def copy(self) -> 'MazeObject':
        """Metoda zwracająca kopię obiektu. Powinna być nadpisana w klasach dziedziczących."""
        raise NotImplementedError("Metoda copy nie jest zaimplementowana.")

    @classmethod
    def create_obj_based_on_char(cls, char : str, pos : Tuple[int, int]) -> 'MazeObject':
        """Funkcja zwracająca obiekt labiryntu na podstawie znaku.

        :param char: Znak reprezentujący obiekt.
        :type char: str
        :param pos: Pozycja obiektu w labiryncie w postaci krotki (x, y).
        :type pos: tuple[int, int]
        :return: Obiekt labiryntu odpowiadający znakowi.
        :rtype: MazeObject
        """
        from .wall import Wall
        from .spawn_manager import SpawnManager
        from .point import Point

        child = cls.character_to_class_mapping.get(char)
        if child is None:
            return None
        
        return child(pos)
        