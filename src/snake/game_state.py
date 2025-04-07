from src.general.agame_state import AGameState
from .snake_dir import Direction as SnakeDir
from queue import Queue

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
