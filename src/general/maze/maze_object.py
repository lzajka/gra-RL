from abc import ABC, abstractmethod
from typing import List

from . import Maze
from typing import Tuple
from numbers import Number
from src.general import Drawable
from decimal import Decimal, ROUND_HALF_UP
import importlib

class MazeObject(Drawable):
    """Klasa abstrakcyjna reprezentująca obiekt znajdujący się w labiryncie.
    """
    character_to_class_mapping = {}
    def __init__(self, position: tuple[Number, Number], parent : Maze):
        """Inicjalizuje obiekt labiryntu na podstawie jego pozycji.

        :param position: Pozycja obiektu w labiryncie w postaci krotki (x, y).
        :type position: tuple[Decimal, Decimal]
        """
        self.maze = parent
        self.position = Decimal(position[0]), Decimal(position[1])
        self.draw()
        
        self.maze._add_object(self)
        


    
    def to_csv_line() -> List[str]:
        return []

    def get_csv_header() -> List[str]:
        return []

    def get_precise_position(self) -> tuple[Decimal, Decimal]:
        """Zwraca dokładną pozycję obiektu. 

        :return: Pozycja obiektu w postaci krotki (x, y).
        :rtype: tuple[Decimal, Decimal]
        """
        return self.position
    
    def get_position(self) -> tuple[int, int]:
        """Zwraca pozycję obiektu w labiryncie. Pozycja ta jest używana przez logikę aktorów (aktor jest albo przypisany do pola, albo nie)

        :return: Pozycja obiektu w postaci krotki (x, y).
        :rtype: tuple[int, int]
        """
        return (self.position[0].to_integral_value(ROUND_HALF_UP), 
                self.position[1].to_integral_value(ROUND_HALF_UP))
    

    def set_position(self, position: tuple[Decimal, Decimal]):
        """Ustawia pozycję obiektu w labiryncie.

        :param position: Nowa pozycja obiektu w postaci krotki (x, y).
        :type position: tuple[Decimal, Decimal]
        """
        self.erase()
        self.maze._remove_object(self)
        self.position = Decimal(position[0]), Decimal(position[1])
        self.draw()
        self.maze._add_object(self)

    def destroy(self):
        """Usuwa obiekt z labiryntu."""
        self.erase()
        self.maze._remove_object(self)


    def _on_update(self):
        """Metoda wywoływana podczas aktualizacji obiektu. Może być nadpisana w klasach dziedziczących."""
        pass

    def _get_color(self):
        """Metoda zwracająca kolor obiektu. Może być nadpisana w klasach dziedziczących."""
        return None

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
    def create_obj_based_on_char(cls, char : str, pos : Tuple[int, int], parent : Maze) -> 'MazeObject':
        """Funkcja zwracająca obiekt labiryntu na podstawie znaku.

        :param char: Znak reprezentujący obiekt.
        :type char: str
        :param pos: Pozycja obiektu w labiryncie w postaci krotki (x, y).
        :type pos: tuple[int, int]
        :param parent: Obiekt labiryntu, do którego należy nowy obiekt.
        :type parent: Maze
        :return: Obiekt labiryntu odpowiadający znakowi.
        :rtype: MazeObject
        """
        child = cls.character_to_class_mapping.get(char) 
        if child is None:
            return None
        
        return child(pos, parent)
        
