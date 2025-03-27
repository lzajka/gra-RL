from abc import ABC, abstractmethod
import pygame

class IGameCore(ABC):
    @abstractmethod
    def restart(self, config):
        pass

    @abstractmethod
    def make_move(self, move):
        pass

    @abstractmethod
    def quit(self):
        pass

    def display_text(self, position, text, font_size = 12, font = None, color=(255, 255, 255), background = 'black'):
        '''Metoda wyświetla tekst na ekranie'''
        if font is None: font = pygame.font.get_default_font()
        if pygame.font.get_fonts().count(font) == 0:
            font = pygame.font.get_default_font()
        
        font = pygame.font.Font(font, font_size)
        img = font.render(text, True, color, background)
        self.screen.blit(img, position)