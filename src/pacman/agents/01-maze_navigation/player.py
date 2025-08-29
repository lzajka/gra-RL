from random import Random
from src.pacman.game_state import GameState
from src.pacman.agents._base import Player as P
from src.pacman.maze_utils import MazeUtils
class Player(P):
    def __init__(self, args, config_overrides = ..., MAX_MEMORY=100_000, BATCH_SIZE=1024, LR=5e-5):
        super().__init__(args, config_overrides, MAX_MEMORY, BATCH_SIZE, LR)
        self.random = Random(10)
        self.hunger = 0
        self.prev_distance = None

    def should_explore(self):
        # Najpierw daj mu wyjść wykonać kilka pierwszych ruchów
        epsilon = max(0.01, 0.75 - self.round_number/128)
        return self.random.random() <= epsilon
    
    def prepare_env(self, state):
        self.hunger = 0
        self.prev_distance = None
        self.prev_collected = 0
        self.state_num = 0
        return super().prepare_env(state)
    
    def can_make_a_decision(self, state):
        # Wykonaj kilka ruchów automatycznie, aby był dalej od środka
        return super().can_make_a_decision(state)

    def visit_state(self, state : GameState):
        if state.is_game_over: return super().visit_state(state)

        pacman_pos = state.a_Pacman.get_position()

        collected = sum(state.collected.values())

        dist = self.maze_utils.get_closest_dist_for_dirs(state, pacman_pos, normalize = False)

        m = min(dist)
        hunger_mercy = False

        if self.prev_distance is None:
            self.prev_distance = m
            hunger_mercy = True

        gotten_closer = m < self.prev_distance

        # Dodatkowo kara czasowa
        state.ai_bonus -= 2

        # Tym mniejsze tym lepsze       
        if self.prev_collected == collected and not gotten_closer and not hunger_mercy:
            self.hunger += 1
            state.ai_bonus -= 5
        elif self.prev_collected < collected:
            self.hunger = 0
        
        if gotten_closer:
            state.ai_bonus += 5


        if self.hunger > 30:
            state.a_Pacman.kill()
        # Ponieważ wynik się zmniejszy zaaktualizuj prev_score
        self.prev_collected = collected
        self.last_visit = state.time_elapsed
        self.prev_distance = m

        return super().visit_state(state)
    
    def on_game_over(self, state):
        self.hunger = 0
        return super().on_game_over(state)
