import pytest
from src.snake.agents.relative_direction.player import map_detection_array
from src.snake.snake_dir import Direction

L = 1
R = 2
U = 3
D = 4
input_arr = [L, R, U, D]


def test_map_left():
    assert map_detection_array(Direction.LEFT, input_arr) == [D, U, L, R]

def test_map_right():
    assert map_detection_array(Direction.RIGHT, input_arr) == [U, D, R, L]

def test_map_up():
    assert map_detection_array(Direction.UP, input_arr) == input_arr

def test_map_down():
    assert map_detection_array(Direction.DOWN, input_arr) == [R, L, D, U]