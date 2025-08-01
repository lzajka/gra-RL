from src.general.aplayer import APlayer
from .game_core import GameCore
from src.pacman.actors import Actor, Pacman, Blinky, Inky, Pinky, Clyde
from argparse import ArgumentParser
import pygame
from .game_state import GameState
from src.general import Direction
from src.pacman.maze.spawn_manager import SpawnManager

class Player(APlayer):
    """Klasa reprezentująca gracza sterowanego przez człowieka
    """
    def __init__(self, args : ArgumentParser, config_overrides : dict = {}):

        super().__init__(args, config_overrides)
        self.pacman : Pacman = None
        self.blinky : Blinky = None
        self.inky : Inky = None


    def getGame(self):
        """Zwraca instancję gry, w której gracz bierze udział.

        :return: Instancja gry.
        :rtype: GameCore
        """
        gc = GameCore.get_main_instance()
        if gc is None:
            gc = GameCore()
        return gc
    
    def make_decision(self, _state):
        """Funkcja podejmująca decyzję na podstawie stanu gry.

        :param state: Obecny stan gry.
        :type state: GameState
        :return: Krotka zawierająca kierunek ruchu i informację o kontynuacji gry.
        :rtype: tuple[Direction, bool]
        """
        # Mimo, że ta funkcja jest po to aby podejmować decyzję, można wsadzić tutaj część logiki gry, która mogłaby być przydatna podczas trenowania modelu
        # Klasy graczy, będą odpowiedzialne, ze inicjalizację aktorów
        if self.pacman is None:
            # Inicjalizacja Pacmana, jeżeli jeszcze nie został zainicjalizowany
            self.pacman = Pacman(self.getGame().maze)
        

        if self.move_number == 0:
            SpawnManager.request_spawn(self.pacman)
        
        elif self.move_number == 5:
            self.blinky = Blinky(self.getGame().maze)
            SpawnManager.request_spawn(self.blinky)

        elif self.move_number == 10:
            self.pinky = Pinky(self.getGame().maze)
            SpawnManager.request_spawn(self.pinky)

        elif self.move_number == 15:
            self.inky = Inky(self.getGame().maze)
            SpawnManager.request_spawn(self.inky)
        
        elif self.move_number == 20:
            self.clyde = Clyde(self.getGame().maze)
            SpawnManager.request_spawn(self.clyde)

        # Obsługa zdarzeń
        events = pygame.event.get()
        controls = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]
        selected_dir = None
        for event in events:
            if event.type == pygame.KEYDOWN and event.key in controls:
                selected_dir = Direction(event.key)
            elif event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return [selected_dir, False]

        return [selected_dir, True]  # Zwraca None jako kierunek i True jako kontynuację gry