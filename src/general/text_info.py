from pygame.font import Font
from typing import Tuple

class TextInfo():
    """Klasa przechowująca informację o tekście
    """

    def __init__(self, font : Font, foreground_color, text_value : str, position : Tuple[int, int]):
        """Konstruktor.

        :param font: Czcionka.
        :type font: Font
        :param foreground_color: Kolor tekstu.
        :type foreground_color: ColorValue
        :param text_value: Tekst.
        :type text_value: str
        :param position: Pozycja
        :type position: Tuple[int, int]
        """
        self.font = font
        self.foreground_color = foreground_color
        self.text_value = text_value
        self.position = position