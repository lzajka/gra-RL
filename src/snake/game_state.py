from src.general.agame_state import AGameState
from .snake_dir import Direction as SnakeDir
from queue import Queue
from typing import Self

class GameState(AGameState):
    score = 0 # używany również jako długość ogona
    is_game_over = False
    events = []
    snake_position = tuple([0, 0])
    snake_tail_queue = Queue()
    snake_tail_set = set() 
    fruit_position = None
    speed = 0
    direction = SnakeDir.RIGHT

    def __init__(self, snake_position):
        self.snake_position = snake_position
        self.snake_tail_queue = Queue()
        self.snake_tail_set = set()
        self.fruit_position = None
        self.direction = SnakeDir.RIGHT

    def copy(self) -> Self:
        copy_state = GameState(self.snake_position)

        copy_state.score = self.score
        copy_state.is_game_over = self.is_game_over
        copy_state.events = self.events.copy()
        copy_state.snake_position = self.snake_position
        copy_state.snake_tail_set = self.snake_tail_set.copy()
        copy_state.fruit_position = self.fruit_position
        copy_state.speed = self.speed
        copy_state.direction = self.direction

        # Kopiowanie kolejki nie jest proste, ponieważ Queue nie ma metody copy()
        copy_state.snake_tail_queue = Queue()
        for item in list(self.snake_tail_queue.queue):
            copy_state.snake_tail_queue.put(item)
        return copy_state

    def to_list(self) -> list:
        return [
            self.score,
            self.snake_position[0],
            self.snake_position[1],
            self.fruit_position[0],
            self.fruit_position[1],
            self.direction.name,
            self.is_game_over,
            self.speed

        ]

    def get_headers(self):
        return [
            'wynik',
            'pozycja_x',
            'pozycja_y',
            'owoc_x',
            'owoc_y',
            'kierunek',
            'czy_koniec',
            'predkosc'
        ]