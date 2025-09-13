from argparse import Namespace
from random import Random
from typing import Dict, List
from src.pacman.ghost_schedule import GhostSchedule
from src.general.maze.maze import Maze
from src.pacman.agents._base import Player as BPlayer
from src.pacman.maze.objects import SpawnManager
from src.general.utils import TupleOperations as TO
from . import config_overrides
from src.pacman.maze_utils import MazeUtils
from src.pacman.game_state import GameState

class Player(BPlayer):
    def __init__(self, args : Namespace, config_overrides = ..., MAX_MEMORY=100_000, BATCH_SIZE=1000, LR=1e-5):
        if args.load_model is None:
            args.load_model = 'models/pacman-02-2-avoid_and_eat.pth'
        super().__init__(args, config_overrides, MAX_MEMORY, BATCH_SIZE, LR)
        self.random = Random(10)
        
    def prepare_env(self, state):
        r = super().prepare_env(state)
        state.set_level(2, schedule=GhostSchedule(1))       # Przywróć normalną prędkość
        SpawnManager.spawn(state.a_Blinky, now=True)
        SpawnManager.spawn(state.a_Pinky)
        self.prev_distance_e = None
        self.prev_distance_ghost : Dict = None
        self.closest_frightened = None
        self.hunger = 0
        self.prev_distance = None
        self.prev_collected = 0

        return r

    def should_explore(self):
        epsilon = max(0.1, 0.3 - self.round_number/512)
        return self.random.random() <= epsilon
    def _reinforce_points(self, state : GameState):

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

        # Tym mniejsze tym lepsze       
        if self.prev_collected == collected and not gotten_closer and not hunger_mercy:
            self.hunger += 1
            state.ai_bonus -= 0.2
        elif self.prev_collected < collected:
            self.hunger = 0
        
        if gotten_closer:
            state.ai_bonus += 0.2


        if self.hunger > 70:
            state.a_Pacman.kill()
        # Ponieważ wynik się zmniejszy zaaktualizuj prev_score
        self.prev_collected = collected
        self.last_visit = state.time_elapsed
        self.prev_distance = m

    def _reinforce_ghosts(self, state : GameState):
        from src.pacman.actors import Ghost
        bonus = 0
        ghosts : List[Ghost] = [state.a_Blinky, state.a_Pinky, state.a_Inky, state.a_Clyde]
        pacman_pos = TO.to_int(state.a_Pacman.get_position())
        mu = self.maze_utils

        energizer_dist = self.maze_utils.distance_to(pacman_pos, 'energizers')
        energizer_reachable = energizer_dist < 1024


        # Dodaj bonus za zbliżenie się do energizera

        egotten_closer = self.prev_distance_e is not None and energizer_dist < self.prev_distance_e and energizer_reachable
        egotten_further = self.prev_distance_e is not None and energizer_dist > self.prev_distance_e and energizer_reachable
        e_stayed = self.prev_distance_e is not None and energizer_dist == self.prev_distance_e and energizer_reachable

        if egotten_closer:
            bonus += 2/(energizer_dist)
        elif egotten_further:
            bonus -= 3/(energizer_dist + 1)
        

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
            # Nie karaj jeżeli jest mało czasu
            remaining_powerup = state.remaining_powerup_time
            if delta_f < 0 and remaining_powerup > 1:
                b = 0.7
                self.log.debug(f'Zbliżono się do przestraszonego ducha: {b}')
                bonus += b

            if delta_f > 0 and remaining_powerup > 1:
                b = -0.7
                self.log.debug(f'Oddalono się od przestraszonego ducha: {b}')
                bonus += b

            # Dodaj karę za zbliżenie się do nieprzestraszonego ducha
            safe_dist = 5
            if delta_d < 0 and ghost_distance['dangerous'] <= safe_dist:
                b = - (safe_dist / (ghost_distance['dangerous'] + 1))
                self.log.debug(f'Zbliżono się do groźnego ducha: {b}')
                bonus += b 

            # Nagroda za oddalenie się

            if delta_d > 0 and ghost_distance['dangerous'] <= 5:
                b = 1.5 * (safe_dist / ghost_distance['dangerous'])
                self.log.debug(f'Oddalono się od groźnego ducha: {b}')
                bonus += b
            
        state.ai_bonus += bonus
        self.prev_distance_e = energizer_dist
        self.prev_distance_ghost = ghost_distance.copy()
    
    def visit_state(self, state):
        self._reinforce_points(state)
        self._reinforce_ghosts(state)

        state.ai_bonus -= 0.3
        return super().visit_state(state)
    
    
    def on_update(self, _state):
        from src.pacman.game_state import GameState
        state : GameState = _state

        if self.move_number == 60*7:
            SpawnManager.spawn(state.a_Inky)
        
        elif self.move_number == 60*15:
            SpawnManager.spawn(state.a_Clyde)

        return super().on_update(state)
