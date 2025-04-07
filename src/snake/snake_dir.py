from enum import Enum
from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT
class Direction(Enum):
    UP = K_UP
    DOWN = K_DOWN
    LEFT = K_LEFT
    RIGHT = K_RIGHT

    def opposite(self):
        '''Metoda zwraca przeciwny kierunek'''
        if self == Direction.UP:
            return Direction.DOWN
        elif self == Direction.DOWN:
            return Direction.UP
        elif self == Direction.LEFT:
            return Direction.RIGHT
        elif self == Direction.RIGHT:
            return Direction.LEFT