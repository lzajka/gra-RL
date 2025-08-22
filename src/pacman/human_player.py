from src.general.aplayer import APlayer
from .game_core import GameCore
from src.pacman.actors import Actor, Pacman, Blinky, Inky, Pinky, Clyde
from argparse import ArgumentParser
import pygame
from .game_state import GameState
from src.general import Direction
from src.pacman.maze.objects import SpawnManager
from typing import Tuple
from .ghost_schedule import GhostSchedule

class Player(APlayer):
    """Klasa reprezentująca gracza sterowanego przez człowieka
    """
    def __init__(self, args : ArgumentParser, config_overrides : dict = {}):

        super().__init__(args, config_overrides)
        self.pacman : Pacman = None
        self.blinky : Blinky = None
        self.inky : Inky = None
        self.prev_state_copy = False


    def getGame(self):
        """Zwraca instancję gry, w której gracz bierze udział.

        :return: Instancja gry.
        :rtype: GameCore
        """
        gc = GameCore.get_main_instance()
        if gc is None:
            gc = GameCore()
        return gc
    
    def event_handling(self) -> Tuple[Direction, bool]:
        events = pygame.event.get()
        controls = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]
        selected_dir = None
        for event in events:
            is_keydown = event.type == pygame.KEYDOWN
            if is_keydown and event.key in controls:
                selected_dir = Direction(event.key)
            elif is_keydown and event.key == pygame.K_d:
                self.maze_utils.debug_display()
            elif event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return [Direction.UP, False]
        return [selected_dir, True]
            
    def can_make_a_decision(self, state : GameState):
        return True

    
    def make_decision(self, _state):
        """Funkcja podejmująca decyzję na podstawie stanu gry.

        :param state: Obecny stan gry.
        :type state: GameState
        :return: Krotka zawierająca kierunek ruchu i informację o kontynuacji gry.
        :rtype: tuple[Direction, bool]
        """
        state : GameState = _state
        from src.pacman.maze_utils import MazeUtils
        #self.maze_utils.debug_display()
        # Mimo, że ta funkcja jest po to aby podejmować decyzję, można wsadzić tutaj część logiki gry, która mogłaby być przydatna podczas trenowania modelu
        # Klasy graczy, będą odpowiedzialne, ze inicjalizację aktorów
        if self.move_number == 0:
            state.set_level(1, schedule=GhostSchedule(1))
            self.pacman = Pacman(state=state)
            self.blinky = Blinky(state=state)
            self.pinky = Pinky(state=state)
            self.inky = Inky(state=state)
            self.clyde = Clyde(state=state)
            self.maze_utils = MazeUtils(state)
            SpawnManager.spawn(self.pacman)
            SpawnManager.spawn(self.blinky, True)
            SpawnManager.spawn(self.pinky)
        
        self.maze_utils.update(self.pacman.get_position())

        if self.move_number == 60*7:
            SpawnManager.spawn(self.inky)
        
        elif self.move_number == 60*15:
            SpawnManager.spawn(self.clyde)

        # Obsługa zdarzeń

        return self.event_handling()