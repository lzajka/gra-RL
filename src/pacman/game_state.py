from src.general import AGameState
from typing import List
import copy as cpy
from .maze import Maze
from copy import deepcopy


class GameState(AGameState):
    def __init__(self, maze : Maze, starting_lives: int = 3):
        """Inicjalizuje stan gry.

        :param maze: Labirynt, w którym rozgrywa się gra.
        :type maze: Maze
        :param starting_lives: Liczba żyć gracza na początku gry.
        :type starting_lives: int, opcjonalnie
        """
        self.remaining_lives = starting_lives
        self.is_game_over = False
        self.score = 0
        self.collected_points = 0
        self.max_points = 0
        self.fps = 2
        self.events = []
        self.maze = maze

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
        maze2 = self.maze.copy()
        gsc = GameState(maze2)
        gsc.remaining_lives = self.remaining_lives
        gsc.is_game_over = self.is_game_over
        gsc.score = self.score
        gsc.collected_points = self.collected_points
        #gsc.remaining_points = self.remaining_points
        gsc.max_points = self.max_points
        gsc.fps = self.fps

    def to_list(self):
        return [
            self.remaining_lives,
            self.is_game_over,
            self.score,
            self.collected_points,
            #self.remaining_points
        ]
    
    @classmethod
    def get_main_instance(cls) -> 'GameState':
        """Zwraca główną instancję stanu gry.
        
        :return: Główna instancja stanu gry.
        :rtype: GameState
        """
        from src.pacman.game_core import GameCore
        gc : GameCore = GameCore.get_main_instance()
        return gc.current_state
    
    def get_headers(self) -> List[str]:
        return [
            'remaining_lives', 
            'is_game_over', 
            'score', 
            'collected_points', 
            #'remaining_points'
            ]

    

    

        


