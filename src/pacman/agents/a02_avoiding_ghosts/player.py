from argparse import Namespace
from random import Random
from typing import List
from src.general.maze.maze import Maze
from src.pacman.agents._base import Player as BPlayer
from src.pacman.maze.objects import SpawnManager
from src.general.utils import TupleOperations as TO
from . import config_overrides

class Player(BPlayer):
    def __init__(self, args : Namespace, config_overrides = ..., MAX_MEMORY=100_000, BATCH_SIZE=512, LR=5e-5):
        if args.load_model is None:
            args.load_model = 'models/pacman-navi.pth'
        super().__init__(args, config_overrides, MAX_MEMORY, BATCH_SIZE, LR)
        self.random = Random(10)

    def should_explore(self):
        epsilon = max(0.1, 0.4 - self.round_number/128/4)
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
        self.prev_distances = [1024] * 4
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
        pacman_pos = TO.to_int(state.a_Pacman.get_position())
        pacman_dir = state.a_Pacman.direction
        mu = self.maze_utils
        distances = []

        for ghost in ghosts:
            ghost_pos = TO.to_int(ghost.get_position())
            how_close = min(mu.navigate_to_position(pacman_pos, ghost_pos, pacman_dir, normalize=False))

            distances.append(how_close)

        # Bonus za przetrwanie

        # Oblicz karę
        for i in range(len(distances)):
            current_distance = distances[i]
            prev_distance = self.prev_distances[i]

            gotten_closer = current_distance < prev_distance
            gotten_farther = current_distance > prev_distance

            proximity = 5

            if current_distance > proximity:
                pass
            elif gotten_closer:
                state.ai_bonus -= 10 / (current_distance + 1)
            elif gotten_farther:
                state.ai_bonus += 5 / (prev_distance + 1)
            
                
        self.prev_distances = distances
        return super().visit_state(state)