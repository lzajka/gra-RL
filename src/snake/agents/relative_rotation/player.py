#!/usr/bin/env python3
from src.snake.agents.default import player as defaultPlayer
from .rotate_direction import RotateDirection
from src.snake.game_core import GameCore
from src.snake.snake_dir import Direction as SnakeDir


class Player(defaultPlayer):
    def rotate(self, direction : RotateDirection):
        """Funkcja do obracania węża w lewo lub w prawo.

        :param direction: Kierunek obrotu węża.
        :type direction: RotateDirection
        """

        game : GameCore = self.game
        current_direction = game.game_state.direction

        new_direction = SnakeDir(4 + {
            SnakeDir.UP: 0,
            SnakeDir.RIGHT: 1,
            SnakeDir.DOWN: 2,
            SnakeDir.LEFT: 3
        }[current_direction] + direction.value % 4)

        