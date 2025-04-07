from abc import ABC, abstractmethod
import pygame

class IGameCore(ABC):
    restart_count = 0
    move_count = 0

    def restart(self, config):
        '''Metoda restartuję grę. Wykorzystuje podaną konfigurację. Zwraca stan gry'''
        self.restart_count += 1
        self.move_count = 0
        return self.on_restart(config)
        

    @abstractmethod
    def on_restart(self, config):
        pass
    
    def make_move(self, move):
        '''Metoda wykonuje ruch'''
        self.move_count += 1
        return self.on_make_move(move)

    @abstractmethod
    def on_make_move(self, move):
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