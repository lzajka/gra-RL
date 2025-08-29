from argparse import Namespace
from random import Random
from typing import Dict, List
from src.general.maze.maze import Maze
from src.pacman.agents._base import Player as BPlayer
from src.pacman.maze.objects import SpawnManager
from src.general.utils import TupleOperations as TO
from . import config_overrides

class Player(BPlayer):
    def __init__(self, args : Namespace, config_overrides = ..., MAX_MEMORY=100_000, BATCH_SIZE=256, LR=5e-5):
        if args.load_model is None:
            args.load_model = 'models/pacman-01-maze_navigation.pth'
        super().__init__(args, config_overrides, MAX_MEMORY, BATCH_SIZE, LR)
        self.random = Random(10)

    def prepare_env(self, state):
        r = super().prepare_env(state)

        # Więcej duchów niż 2 to za dużo
        SpawnManager.spawn(state.a_Blinky, now=True)
        SpawnManager.spawn(state.a_Pinky, now = True)
        self.prev_distance_e = None
        self.prev_distance_ghost : Dict = None
        self.closest_frightened = None

        return r
    
    def _get_powerpellet_info(self, state, mu, intersection):
        arr = super()._get_powerpellet_info(state, mu, intersection)

        # Popraw ilość energizerów
        arr[0] = arr[0] * 4

        return arr

    def should_explore(self):
        epsilon = max(0.01, 0.5 - self.round_number/512)
        return self.random.random() <= epsilon
    
    def visit_state(self, state):
        from src.pacman.actors import Ghost

        ghosts : List[Ghost] = [state.a_Blinky, state.a_Pinky, state.a_Inky, state.a_Clyde]
        pacman_pos = TO.to_int(state.a_Pacman.get_position())
        mu = self.maze_utils
        bonus = 0


        energizer_dist = self.maze_utils.distance_to(pacman_pos, 'energizers')
        energizer_reachable = energizer_dist < 1024


        # Dodaj bonus za zbliżenie się do energizera

        egotten_closer = self.prev_distance_e is not None and energizer_dist < self.prev_distance_e and energizer_reachable
        egotten_further = self.prev_distance_e is not None and energizer_dist > self.prev_distance_e and energizer_reachable
        e_stayed = self.prev_distance_e is not None and energizer_dist == self.prev_distance_e and energizer_reachable

        if egotten_closer:
            bonus += 50
        elif egotten_further:
            bonus -= 60
        

        # Oblicz odległości między różnymi aktywnymi typami duchów
        ghost_distance = {
            'frightened': 1024,
            'dangerous': 1024
        }

        for g in ghosts:
            is_frightened = g.is_frightened
            is_active = not g.is_dead and g.is_spawned
            pos = TO.to_int(g.get_position())

            if not is_active: continue

            dist = mu.distance_to(pacman_pos, pos)

            ghost_str = 'frightened' if is_frightened else 'dangerous'
            
            ghost_distance[ghost_str] = min(ghost_distance[ghost_str], dist)

        # Oblicz w jakim stopniu się zbliżono

        if self.prev_distance_ghost is not None:
            delta_f = ghost_distance['frightened'] - self.prev_distance_ghost['frightened']
            delta_d = ghost_distance['dangerous'] - self.prev_distance_ghost['dangerous']
            # Dodaj bonus za zbliżenie się do przestraszonego ducha

            if delta_f < 0:
                bonus += 200 / (ghost_distance['frightened'] + 1)

            # Dodaj karę za zbliżenie się do nieprzestraszonego ducha

            if delta_d < 0 and ghost_distance['dangerous'] <= 5:
                bonus -= 200 / (ghost_distance['dangerous'] + 1)
        


        state.ai_bonus += bonus
        self.prev_distance_e = energizer_dist
        self.prev_distance_ghost = ghost_distance.copy()
        return super().visit_state(state)
    
    
    def on_update(self, _state):
        from src.pacman.game_state import GameState
        state : GameState = _state

        return super().on_update(state)
