from random import Random
from src.pacman.agents._base import Player as P

class Player(P):
    def __init__(self, args, config_overrides = ..., MAX_MEMORY=100000, BATCH_SIZE=1000, LR=0.001):
        super().__init__(args, config_overrides, MAX_MEMORY, BATCH_SIZE, LR)
        self.random = Random(10)
        self.last_visit = 0
        self.prev_score = 0
        self.hunger = 0

    def should_explore(self):
        epsilon = 80 - self.round_number
        return self.random.randint(0, 200) < epsilon
    
    def visit_state(self, state):
        current_score = state.score

        if current_score == self.prev_score:
            delta = state.time_elapsed - self.last_visit
            self.hunger += 1
            state.score -= 10
        else:
            self.hunger = 0
            
        if self.hunger >= 7:
            state.is_game_over = True
        # Ponieważ wynik się zmniejszy zaaktualizuj prev_score
        self.prev_score = state.score
        self.last_visit = state.time_elapsed 

        return super().visit_state(state)
    
    def on_game_over(self, state):
        self.hunger = 0
        return super().on_game_over(state)
    
