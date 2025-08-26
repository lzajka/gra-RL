from random import Random
from src.pacman.game_state import GameState
from src.pacman.agents._base import Player as P
from src.pacman.maze_utils import MazeUtils
class Player(P):
    def __init__(self, args, config_overrides = ..., MAX_MEMORY=100_000, BATCH_SIZE=32, LR=5e-4):
        super().__init__(args, config_overrides, MAX_MEMORY, BATCH_SIZE, LR)
        self.random = Random(10)
        self.last_visit = 0
        self.prev_collected = 0
        self.hunger = 0
        self.prev_distance = -1

    def should_explore(self):
        epsilon = min(0.1, 1 - self.round_number/64)
        return self.random.random() <= epsilon
    
    def prepare_env(self, state):
        self.hunger = 0
        self.prev_distance = -1
        return super().prepare_env(state)

    def visit_state(self, state : GameState):
        if state.is_game_over: return super().visit_state(state)

        intersection = state.maze.shift_position(state.a_Pacman.get_position(), state.a_Pacman.direction)
        if state.maze.check_wall(intersection): intersection = state.a_Pacman.get_position()

        collected = sum(state.collected.values())

        dist = self.maze_utils.get_shortest_distances_from_intersection(state, intersection)

        m = max(dist)

        # Tym mniejsze tym gorsze, dlatego chcemy ciągle to zwiększać
        gotten_closer = m > self.prev_distance

        if self.prev_collected == collected and not gotten_closer:
            self.hunger += 1
            state.ai_bonus -= 10
        elif self.prev_collected < collected:
            self.hunger = 0

        if self.hunger > 3:
            state.a_Pacman.kill()
        # Ponieważ wynik się zmniejszy zaaktualizuj prev_score
        self.prev_collected = collected
        self.last_visit = state.time_elapsed
        self.prev_distance = m

        return super().visit_state(state)
    
    def on_game_over(self, state):
        self.hunger = 0
        return super().on_game_over(state)
    
    def state_to_arr(self, state, mu):
        # Ponieważ na razie pozostałe cechy są nam obojętne mozna się ich pozbyć
        ret = super().state_to_arr(state, mu)
        for i in range(len(ret) - 4):
            ret[i] = 0

        return ret