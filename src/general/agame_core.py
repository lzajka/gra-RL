from abc import ABC, abstractmethod
import pygame
from . import agame_state
from typing import Tuple


class AGameCore(ABC):

    def restart(self, config) -> agame_state.AGameState:
        '''Metoda restartuję grę. Wykorzystuje podaną konfigurację. Zwraca stan gry'''
        self.move_count = 0

        self.texts_prev = dict()
        self.texts_value = dict()
        self.texts_font_size = None
        self.texts_font = dict()
        self.texts_foreground = dict()
        self.texts_background = dict()



        return self.on_restart(config)
        

    @abstractmethod
    def on_restart(self, config):
        pass
    
    def make_move(self, move) -> Tuple[agame_state.AGameState, bool]:
        '''Metoda wykonuje ruch'''
        return self.on_make_move(move)

    @abstractmethod
    def on_make_move(self, move):
        pass

    @abstractmethod
    def quit(self):
        pass
    
    def display_text(self, position : Tuple[int, int], text, font_size = 12, font = None, color=(255, 255, 255), background = 'black'):

        # Wczytaj czcionkę
        if font is None: font = pygame.font.get_default_font()
        if pygame.font.get_fonts().count(font) == 0:
            font = pygame.font.get_default_font()
        self.texts_font = font

        # Zapisz tekst
        self.texts_value[position] = text
        self.texts_font_size = font_size
        self.texts_foreground[position] = color
        self.texts_background[position] = background

    def __render_texts(self):
        '''Metoda wyświetla teksty na ekranie'''
        for position in self.texts_value:
            self.__render_text(position)

    def __render_text(self, position : Tuple[int, int]):
        '''Metoda wyświetla tekst na ekranie'''

        # Wczytaj dane
        text = self.texts_value[position]
        font_size = self.texts_font_size
        font = self.texts_font
        color = self.texts_foreground[position]
        background = self.texts_background[position]

        # Jeżeli tekst był wcześniej wypisywany w tym miejscu, to przywróć to co wcześniej było w tym miejscu
        self.clear_text(position)
        
        font = pygame.font.Font(font, font_size)

        # Zapisz to co jeszcze jest w tym miejscu
        self.texts_prev[position] = self.screen.subsurface((position[0], position[1], font.size(text)[0], font.size(text)[1])).copy()

        # Wyświetl tekst
        img = font.render(text, True, color, background)
        self.screen.blit(img, position)

    def clear_text(self, position : Tuple[int, int]):
        '''Metoda czyści tekst w danym miejscu'''
        if position in self.texts_prev:
            self.screen.blit(self.texts_prev[position], position)
            self.texts_prev.pop(position)

    def draw_box(self, pos, color, cell_size = None):
        '''Metoda rysuje kwadrat o podanym kolorze na podanej pozycji'''
        [left, top] = pos
        width = cell_size
        leftpx = left * width
        toppx = top * width
        pygame.draw.rect(self.screen,color, pygame.Rect(leftpx, toppx, width, width))
    
    def render(self):
        '''Metoda renderuje ekran'''
        # Zaktualizuj tekst, jeżeli się zmienił
        self.__render_texts()

        # Zaktualizuj ekran
        pygame.display.update()
    
    @abstractmethod
    def get_default_config(self):
        pass
    
    def show_score(self):
        self.__render_texts(tuple([0, 0]), f'Wynik: {self.game_state.score}', self.config.SCORE_FONT_SIZE, self.config.SCORE_FONT, self.config.SCORE_FONT_COLOR)
