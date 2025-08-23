from src.general import AGameState
from typing import List
import copy as cpy
from src.general.maze import Maze
from copy import deepcopy


class GameState(AGameState):
    def __init__(self, starting_lives: int = 3):
        from src.pacman.actors import Blinky, Pinky, Inky, Clyde, Pacman
        """Inicjalizuje stan gry.

        :param maze: Labirynt, w którym rozgrywa się gra.
        :type maze: Maze
        :param starting_lives: Liczba żyć gracza na początku gry.
        :type starting_lives: int, opcjonalnie
        """
        self.remaining_lives = starting_lives
        self.is_game_over = False
        self.score = 0
        self.collected = {
            'point': 0,
            'energizer': 0
        }
        self.max_points = 0
        self.fps = 60
        self.events = []
        self.maze = None
        self.level = 1
        self.round = 0
        self.frame = 0
        self.time_elapsed = 0.0                     # Czas w sekundach
        self.a_Blinky : Blinky = None
        self.a_Pinky : Pinky = None
        self.a_Inky : Inky = None
        self.a_Clyde : Clyde = None
        self.a_Pacman : Pacman = None
        self.powerup_activate_start = 0.0
        self.powerup_duration = 0.0
        self.schedule = None    

    def to_training_array(self) -> List[float]:
        """Zwraca stan gry jako tablicę do treningu.
        :return: Tablica z wartościami stanu gry.
        :rtype: List[float]
        """
        pass

    def copy(self) -> 'GameState':
        """Tworzy kopię stanu gry. Nie wszystkie elementy są kopiowane - elementy niezmienne, takie jak ściany nie są kopiowane.

        :return: Kopia stanu gry.
        :rtype: GameState
        """
        
        gsc = GameState()
        maze2 = self.maze.copy(gsc)
        gsc.maze = self.maze
        gsc.remaining_lives = self.remaining_lives
        gsc.is_game_over = self.is_game_over
        gsc.score = self.score
        gsc.collected = self.collected
        gsc.max_points = self.max_points
        gsc.fps = self.fps
        gsc.round = self.round
        gsc.level = self.level
        gsc.time_elapsed = self.time_elapsed
        gsc.frame = self.frame
        gsc.max_points = self.max_points
        gsc.schedule = self.schedule
        gsc.powerup_activate_start = self.powerup_activate_start
        gsc.powerup_duration = self.powerup_duration
        # Aktorów nie kopiujemy. nowe wartości zostaną ustawione podczas wykonywania kopii labiryntu

        return gsc

    def to_list(self):
        return [
            self.is_game_over,
            self.score,
            self.collected
        ]
    
    @classmethod
    def get_main_instance(cls) -> 'GameState':
        """Zwraca główną instancję stanu gry.
        
        :return: Główna instancja stanu gry.
        :rtype: GameState
        """
        from src.pacman.game_core import GameCore
        gc : GameCore = GameCore.get_main_instance()
        return gc.game_state
    
    def get_headers(self) -> List[str]:
        return [
            'remaining_lives', 
            'is_game_over', 
            'score', 
            'collected_points', 
            #'remaining_points'
            ]
    
    def set_level(self, level, schedule):
        self.schedule = schedule
        self.level = level

    
    @property
    def remaining_powerup_time(self):
        remaining_time = self.powerup_duration + self.time_elapsed - self.powerup_activate_start
        if self.powerup_duration <= 0 or remaining_time <= 0: return 0

        normalized_time = remaining_time/self.powerup_duration
        return normalized_time
    

        


