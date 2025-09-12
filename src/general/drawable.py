from abc import ABC, abstractmethod
from .agame_core import AGameCore
from typing import Tuple

class Drawable(ABC):
    """
    Klasa abstrakcyjna reprezentująca obiekt, który może być rysowany na ekranie gry.
    """


    def get_position(self) -> tuple[float, float]:
        return None
    
    def get_precise_position(self) -> tuple[float, float]:
        """Zwraca pozycję obiektu w postaci krotki (x, y).

        :return: Pozycja obiektu.
        :rtype: tuple[float, float]
        """
        return None
    
    def _pos(self) -> Tuple[float, float]:
        prec_pos = self.get_precise_position()
        int_pos = self.get_position()

        if prec_pos is not None:
            return float(prec_pos[0]), float(prec_pos[1])
        elif int_pos is not None:
            return float(prec_pos[0]), float(prec_pos[1])
        else:
            raise NotImplementedError('Przynajmniej jedna z metod get_position oraz get_precise_position musi zostać zaimplementowana')


    @abstractmethod
    def _get_filled_ratio(self) -> int:
        """Zwraca rozmiar obiektu w postaci długości boku kwadratu.

        :return: Rozmiar obiektu.
        :rtype: int
        """
        pass

    @abstractmethod
    def _get_color(self) -> tuple[int, int, int]:
        """Zwraca kolor obiektu w postaci krotki (R, G, B).

        :return: Kolor obiektu.
        :rtype: tuple[int, int, int]
        """
        pass


    @abstractmethod
    def _get_named_layer(self) -> str:
        """Zwraca nazwę warstwy, na której obiekt powinien być rysowany.

        :return: Nazwa warstwy.
        :rtype: str
        """
        pass

    @abstractmethod
    def _get_game_core(self) -> 'AGameCore':
        """Zwraca instancję gry, w której obiekt jest rysowany.

        :return: Instancja gry.
        :rtype: AGameCore
        """
        pass

    @abstractmethod
    def _get_grid_cell_size(self) -> int:
        """Zwraca rozmiar komórki siatki w pikselach.

        :return: Rozmiar komórki siatki.
        :rtype: int
        """
        pass


    def draw(self):
        """Rysuje obiekt na ekranie."""
        color = self._get_color()
        if color is None:
            return
        game_core = self._get_game_core()
        position = self._pos()
        filled_ratio = self._get_filled_ratio()
        layer = self._get_named_layer()
        cell_size = self._get_grid_cell_size()

        game_core.draw_box(position, color, cell_size , layer, filled_ratio)

    def erase(self):
        """Czyści obiekt z ekranu."""
        if self._get_color() is None:
            return
        game_core = self._get_game_core()
        position = self._pos()
        filled_ratio = self._get_filled_ratio()
        color = (0, 0, 0, 0)
        layer = self._get_named_layer()
        cell_size = self._get_grid_cell_size()

        game_core.draw_box(position, color, cell_size , layer, filled_ratio)
    
