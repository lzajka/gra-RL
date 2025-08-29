from argparse import Namespace
from random import Random
from typing import Dict, List
from src.pacman.game_state import GameState
from src.general.maze.maze import Maze
from src.pacman.agents._base import Player as BPlayer
from src.pacman.maze.objects import SpawnManager
from src.general.utils import TupleOperations as TO
from . import config_overrides
import src.pacman.timer as t

class Player(BPlayer):
    def __init__(self, args : Namespace, config_overrides = ..., MAX_MEMORY=100_000, BATCH_SIZE=256, LR=5e-5):
        if args.load_model is None:
            args.load_model = 'models/pacman-02-2-avoid_and_eat.pth'
        super().__init__(args, config_overrides, MAX_MEMORY, BATCH_SIZE, LR)
        self.random = Random(10)

    def prepare_env(self, state):
        r = super().prepare_env(state)

        SpawnManager.spawn(state.a_Blinky, now=True)
        SpawnManager.spawn(state.a_Pinky)
        t.start_time_timer(5, lambda s : SpawnManager.spawn(s.a_Inky))
        t.start_time_timer(15, lambda s : SpawnManager.spawn(s.a_Clyde))

        #self.prev_score = 0
        #self.hunger = 0
        #self.prev_distance = None
        #self.prev_score = 0

        return r
    

    def should_explore(self):
        epsilon = max(0.01, 0.3 * (1 - self.round_number/128))
        return self.random.random() <= epsilon
    
    
    def on_update(self, _state):
        from src.pacman.game_state import GameState
        state : GameState = _state

        return super().on_update(state)
