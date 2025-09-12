from argparse import Namespace
from random import Random
from typing import Dict, List
from src.general.maze.maze import Maze
from src.pacman.agents._base import Player as BPlayer
from src.pacman.maze.objects import SpawnManager
from src.general.utils import TupleOperations as TO
from . import config_overrides
from src.pacman.maze_utils import MazeUtils
from src.pacman.game_state import GameState

class Player(BPlayer):
    def __init__(self, args : Namespace, config_overrides = ..., MAX_MEMORY=100_000, BATCH_SIZE=1000, LR=5e-5):
        if args.load_model is None:
            args.load_model = 'models/pacman-01-maze_navigation.pth'
        super().__init__(args, config_overrides, MAX_MEMORY, BATCH_SIZE, LR)
        self.random = Random(10)

    def _randomize_positions(self, state : GameState):
        from src.pacman.game_config import GameConfig
        from src.pacman.maze.objects.spawn_manager import GhostSpawner, PacmanSpawner
        from src.general import Direction
        # Spawn ducha musi mieć wolną lewą stronę
        # Spawn gracza 
        mu = self.maze_utils
        maze = state.maze

        gc : GameConfig = self.game_config
        prox = gc.SGHOST_CLOSEST_PROX_TO_SPLAYER
        maze_dim = maze.get_size()

        player_spawn = (0,0)
        ghost_spawn = (0,0)

        # Spawn pacmana może być wszędzie, gdzie nie ma ściany.
        while maze.check_wall(player_spawn):
            player_spawn = (self._random.randrange(maze_dim[0]), self._random.randrange(maze_dim[1]))

        # Spawn ducha musi być odpowiednio oddalony od spawnu pacmana, musi nie znajdować się w ściany, oraz blok po jego lewej stronie również nie może znajdować się w ścianie.
        while (maze.check_wall(ghost_spawn) 
               or maze.check_wall(maze.shift_position(ghost_spawn, Direction.LEFT)) 
               or self.maze_utils.distance_to(player_spawn, ghost_spawn) < prox):
            ghost_spawn = (self._random.randrange(maze_dim[0]), self._random.randrange(maze_dim[1]))
        
        # Ustaw pozycję spawnerów.
        PacmanSpawner.instance.set_position(player_spawn)
        GhostSpawner.instance.set_position(ghost_spawn)

        # Ponieważ pacman jest już zespawnowany - zmień jego pozycję
        state.a_Pacman.set_position(player_spawn)
        
    def prepare_env(self, state):
        r = super().prepare_env(state)
        self._randomize_positions(state)
        SpawnManager.spawn(state.a_Blinky, now=True)
        self.prev_distance_e = None
        self.prev_distance_ghost : Dict = None
        self.closest_frightened = None
        self.hunger = 0
        self.prev_distance = None
        self.prev_collected = 0

        return r

    def should_explore(self):
        epsilon = max(0.1, 0.5 - self.round_number/512)
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
            state.ai_bonus -= 15
        elif self.prev_collected < collected:
            self.hunger = 0
        
        if gotten_closer:
            state.ai_bonus += 10


        if self.hunger > 70:
            state.a_Pacman.kill()
        # Ponieważ wynik się zmniejszy zaaktualizuj prev_score
        self.prev_collected = collected
        self.last_visit = state.time_elapsed
        self.prev_distance = m

    def visit_state(self, state):
        from src.pacman.actors import Ghost

        ghosts : List[Ghost] = [state.a_Blinky, state.a_Pinky, state.a_Inky, state.a_Clyde]
        pacman_pos = TO.to_int(state.a_Pacman.get_position())
        mu = self.maze_utils
        bonus = 0

        self._reinforce_points(state)
        energizer_dist = self.maze_utils.distance_to(pacman_pos, 'energizers')
        energizer_reachable = energizer_dist < 1024


        # Dodaj bonus za zbliżenie się do energizera

        egotten_closer = self.prev_distance_e is not None and energizer_dist < self.prev_distance_e and energizer_reachable
        egotten_further = self.prev_distance_e is not None and energizer_dist > self.prev_distance_e and energizer_reachable
        e_stayed = self.prev_distance_e is not None and energizer_dist == self.prev_distance_e and energizer_reachable

        if egotten_closer:
            bonus += 20/energizer_dist
        elif egotten_further:
            bonus -= 25/(energizer_dist + 1)
        

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
                bonus += 150 / (ghost_distance['frightened'] + 5)

            if delta_f > 0 and remaining_powerup > 1:
                bonus -= 175 / (ghost_distance['frightened'] + 5)

            # Dodaj karę za zbliżenie się do nieprzestraszonego ducha

            if delta_d < 0 and ghost_distance['dangerous'] <= 5:
                bonus -= 175 / (ghost_distance['dangerous'] + 4)

            # Nagroda za oddalenie się

            if delta_d > 0 and ghost_distance['dangerous'] <= 5:
                bonus += 150 / (ghost_distance['dangerous'] + 4)
            
            # Kara czasowa
            bonus -= 1


        state.ai_bonus += bonus
        self.prev_distance_e = energizer_dist
        self.prev_distance_ghost = ghost_distance.copy()
        return super().visit_state(state)
    
    
    def on_update(self, _state):
        from src.pacman.game_state import GameState
        state : GameState = _state

        return super().on_update(state)
