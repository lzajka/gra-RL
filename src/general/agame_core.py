from abc import ABC, abstractmethod
import pygame
from .agame_state import AGameState
from typing import Tuple
from pygame.surface import Surface
from logging import getLogger
from typing import List, Dict, Tuple
from .text_info import TextInfo

class AGameCore(ABC):

    def __init__(self, window_dimensions : Tuple[int, int] , surface_order = []):
        """Metoda inicjalizująca AGameCore. Ustawia również `surface_order`, który tworzy potrzebne warstwy.

        :param window_dimensions: Wymiary okna
        :type window_dimensions: Tuple[int, int]
        :param surface_order: Lista przedstawiająca kolejność nazwanych warstw - warstwy występujące wcześniej są pod warstwami występującymi później. Oprócz wymienionych wcześniej warstw zostaną utworzone warstwy `root` (na początku) oraz `text` (na końcu).
        :type surface_order: list, optional
        """

        pygame.init()

        self.window_dimensions = window_dimensions
        self.surface_dict : Dict[str, Surface] = dict()
        self.surface_dict['root'] = pygame.display.set_mode(window_dimensions)

        self.root_surface = self.surface_dict['root']
        self.surface_order = surface_order + ['text']

        # Zmienne potrzebne do wyświetlania tekstu
        self.text : Dict[Tuple[int,int], TextInfo] = dict()
        
        
    # Warstwy

    def _set_cell_size(self, cell_size : int):
        """Metoda ustawia rozmiar komórki w pikselach.
        """


    def __make_surfaces(self):
        """Metoda tworzy powierzchnie (`Surface`) na podstawie `surface_order` podanego podczas inicjalizacji.
        Warstwy występujące wcześniej są pod warstwami występującymi później.
        """
        

        for surface_name in self.surface_order:

            self.surface_dict[surface_name] = Surface(self.window_dimensions, pygame.SRCALPHA, 32)

        

    # Restart

    def restart(self, config) -> AGameState:
        '''Metoda restartuję grę. Wykorzystuje podaną konfigurację. Zwraca stan gry'''
        self.move_count = 0
        self.text : Dict[Tuple[int,int], TextInfo] = dict()      

        self.__make_surfaces()
        
        return self.on_restart(config)

        
    # Handlery

    @abstractmethod
    def on_restart(self, config):
        pass
    
    def make_move(self, move) -> Tuple[AGameState, bool]:
        '''Metoda wykonuje ruch'''
        return self.on_make_move(move)

    @abstractmethod
    def on_make_move(self, move):
        pass
    
    # Wyjście

    @abstractmethod
    def quit(self):
        pass    

    # Funkcje rysownicze

    def display_text(self, position : Tuple[int, int], text, font_size = 12, font = None, foreground = 'white'):
        """Metoda wyświetlająca, lub aktualizująca tekst.

        :param position: Pozycja tekstu. Uzywana również jako identyfikator.
        :type position: Tuple[int, int]
        :param text: Zawartość tekstu.
        :type text: str
        :param font_size: Rozmiar czcionki, domyślnie 12
        :type font_size: int, opcjonalny
        :param font: Czcionka
        :type font: FileArg, opcjonalny

        """
        # Wczytaj czcionkę
        if font is None: font = pygame.font.get_default_font()
        if pygame.font.get_fonts().count(font) == 0:
            font = pygame.font.get_default_font()

        f = pygame.font.Font(font, font_size)
        # Zapisz tekst
        self.text[position] = TextInfo(
            font=f,
            foreground_color=foreground,
            text_value=text,
            position=position
        )

        self.__make_text_surface()

    def __make_text_surface(self):
        text_surface = self.surface_dict['text']

        # Wyczyść
        text_surface.fill((0,0,0,0))

        # render
        for pos in self.text.keys():
            text_info = self.text[pos]
            img = text_info.font.render(text_info.text_value, True, text_info.foreground_color, None)
            text_surface.blit(img, pos)
    
    def _get_cell_size(self) -> int:
        """Metoda zwraca rozmiar komórki planszy w pikselach"""
        pass 


    def draw_box(self, pos : Tuple[int, int], color, cell_size : int = None, id : str = 'root', filled_ratio : float = 1):
        """Metoda rysuje kwadrat na podanej pozycji

        :param pos: Pozycja
        :type pos: Tuple[int, int]
        :param color: Kolor
        :type color: ColorValue
        :param cell_size: Bok kwadratu w px
        :type cell_size: int
        :param id: Nazwa warstwy na której kwadrat ma zostać namalowany. Domyślnie 'root'
        :type id: str
        :param filled_ratio: Stosunek wypełnienia kwadratu. Domyślnie 1 (pełne wypełnienie)
        :type filled_ratio: float
        """
        [left, top] = pos
        size = cell_size


        filled_size = size * filled_ratio

        offset = (size - filled_size) // 2

        leftpx = left * size + offset
        toppx = top * size + offset
        surface = self.surface_dict[id]
        pygame.draw.rect(surface, color, pygame.Rect(leftpx, toppx, filled_size, filled_size))


    def show_score(self):
        self.display_text(tuple([0, 0]), f'Wynik: {self.game_state.score}', self.config.SCORE_FONT_SIZE, self.config.SCORE_FONT, self.config.SCORE_FONT_COLOR)

    # Funkcja renderująca

    def render(self):
        '''Metoda renderuje ekran'''
        # Narysuj warstwy
        for surface_name in self.surface_order:
            surface : Surface = self.surface_dict[surface_name]
            self.root_surface.blit(surface, (0,0))
        
        # Zaktualizuj ekran
        pygame.display.update()
    def fill_layer(self, layer_name : str, color : tuple[int, int, int]):
        """Metoda wypełnia warstwę kolorem.

        :param layer_name: Nazwa warstwy
        :type layer_name: str
        :param color: Kolor wypełnienia
        :type color: tuple[int, int, int]
        """
        
        self.surface_dict[layer_name].fill(color)
    # Pozostałe

    @abstractmethod
    def get_default_config(self):
        pass
    
