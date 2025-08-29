from argparse import Namespace
from random import Random
from typing import List
from src.general.maze.maze import Maze
from src.pacman.agents._base import Player as BPlayer
from src.pacman.maze.objects import SpawnManager
from src.general.utils import TupleOperations as TO
from . import config_overrides

class Player(BPlayer):
    def __init__(self, args : Namespace, config_overrides = ..., MAX_MEMORY=100_000, BATCH_SIZE=2048, LR=1e-5):
        if args.load_model is None:
            args.load_model = 'models/pacman-02-avoiding.pth'
        super().__init__(args, config_overrides, MAX_MEMORY, BATCH_SIZE, LR)
        self.random = Random(10)

    def prepare_env(self, state):
        r = super().prepare_env(state)

        self.spawn_flag = 0
        SpawnManager.spawn(state.a_Blinky, now=True)
        SpawnManager.spawn(state.a_Pinky, now = True)
        SpawnManager.spawn(state.a_Inky, now = True)
        SpawnManager.spawn(state.a_Clyde, now = True)
        self.prev_distance_e = None
        self.closest_frightened = None

        return r
    
    def _get_powerpellet_info(self, state, mu, intersection):
        arr = super()._get_powerpellet_info(state, mu, intersection)

        # Popraw ilość energizerów
        arr[0] = arr[0] * 4

        return arr

    def should_explore(self):
        epsilon = max(0.01, 0.5 - self.round_number/256)
        return self.random.random() <= epsilon
    
    def visit_state(self, state):

        pacman_pos = TO.to_int(state.a_Pacman.get_position())

        dist = self.maze_utils.distance_to(pacman_pos, 'energizers')

        ghosts = [state.a_Blinky, state.a_Pinky, state.a_Inky, state.a_Clyde]

        bonus = 0


        if self.prev_distance_e is not None and dist < self.prev_distance_e:
            bonus += 200
        else:
            bonus -= 100
        
        state.ai_bonus += bonus
        self.prev_distance_e = dist
        
        return super().visit_state(state)
    
    
    def on_update(self, _state):
        from src.pacman.game_state import GameState
        state : GameState = _state

        return super().on_update(state)
