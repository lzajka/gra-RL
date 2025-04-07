from enum import Enum
from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT
class Direction(Enum):
    UP = K_UP
    DOWN = K_DOWN
    LEFT = K_LEFT
    RIGHT = K_RIGHT