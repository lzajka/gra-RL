from argparse import Namespace
from random import Random
from typing import List
from src.general.maze.maze import Maze
from src.pacman.agents._base import Player as BPlayer
from src.pacman.maze.objects import SpawnManager
from src.general.utils import TupleOperations as TO

class Player(BPlayer):
    def __init__(self, args : Namespace, config_overrides = ..., MAX_MEMORY=100_000, BATCH_SIZE=64, LR=5e-5):
        if args.load_model is None:
            args.load_model = 'models/pacman-navi.pth'
        super().__init__(args, config_overrides, MAX_MEMORY, BATCH_SIZE, LR)
        self.random = Random(10)

    def should_explore(self):
        epsilon = min(0.1, 0.7 - self.round_number/1024)
        return self.random.random() <= epsilon
    
    def prepare_env(self, state):
        from src.pacman.maze.objects import Energizer
        self.prev_collected = 0
        self.hunger = 0
        ret = super().prepare_env(state)
        # Zablokuj energizery
        maze : Maze = state.maze
        cells = maze.get_all_objects()
        energizers = []
        for cell in cells:
            for o in list(cell):
                if isinstance(o, Energizer): energizers.append(o)

        for energizer in energizers:
            energizer.destroy()
        # Zespawnuj blinky'ego
        SpawnManager.spawn(state.a_Blinky, now=True)
        SpawnManager.spawn(state.a_Pinky)
        self.spawn_flag = 0
        return ret
    
    def on_update(self, _state):
        from src.pacman.game_state import GameState
        state : GameState = _state
        if state.time_elapsed > 10 and self.spawn_flag == 0:
            SpawnManager.spawn(state.a_Inky)
            self.spawn_flag += 1
        elif state.time_elapsed > 20 and self.spawn_flag == 1:
            SpawnManager.spawn(state.a_Clyde)
            self.spawn_flag += 1

        return super().on_update(state)

    def visit_state(self, state):
        from src.pacman.actors import Ghost
        ghosts : List[Ghost] = [state.a_Blinky , state.a_Pinky, state.a_Inky, state.a_Clyde]
        pacman_pos = state.a_Pacman.get_position()

        distances = []

        for ghost in ghosts:
            pos = ghost.get_position()

            dist = abs(pacman_pos[0] - pos[0]) + abs(pacman_pos[1] - pos[1])

            distances.append(dist)

        # Oblicz karę
        for distance in distances:
            if distance < 15:
                state.ai_bonus -= 50/(distance/5+1)

        return super().visit_state(state)