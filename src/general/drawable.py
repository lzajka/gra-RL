from abc import ABC, abstractmethod
from .agame_core import AGameCore

class Drawable(ABC):
    """
    Klasa abstrakcyjna reprezentująca obiekt, który może być rysowany na ekranie gry.
    """

    @abstractmethod
    def get_position(self) -> tuple[int, int]:
        """Zwraca pozycję obiektu w postaci krotki (x, y).

        :return: Pozycja obiektu.
        :rtype: tuple[int, int]
        """
        pass

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
        game_core = self._get_game_core()
        position = self.get_position()
        filled_ratio = self._get_filled_ratio()
        color = self._get_color()
        layer = self._get_named_layer()
        cell_size = self._get_grid_cell_size()

        game_core.draw_box(position, color, cell_size , layer, filled_ratio)

    def erase(self):
        """Czyści obiekt z ekranu."""
        game_core = self._get_game_core()
        position = self.get_position()
        filled_ratio = self._get_filled_ratio()
        color = (0, 0, 0, 0)
        layer = self._get_named_layer()
        cell_size = self._get_grid_cell_size()

        game_core.draw_box(position, color, cell_size , layer, filled_ratio)
    
