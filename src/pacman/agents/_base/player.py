#!/usr/bin/env python3

from abc import abstractmethod
from decimal import Decimal
from src.general.maze.maze import Position
from src.pacman.game_core import GameCore
from src.pacman.game_config import GameConfig
from . import config_overrides
from src.general import APlayer, Direction
from src.general.maze import Maze
from src.pacman.game_state import GameState
from .model import Linear_QNet
from .trainer import QTrainer
from src.pacman.agents._base.stats_display import StatsDisplay
from src.pacman.actors import Pacman, Blinky, Pinky, Inky, Clyde
from typing import List, Tuple
from src.pacman.maze_utils import MazeUtils
from src.pacman.ghost_schedule import GhostSchedule
from src.general.direction import Direction
from src.general.utils import TupleOperations as TO

import pygame
import torch
import random
import numpy as np
from collections import deque
from logging import getLogger



from argparse import ArgumentParser
class Player(APlayer):

    cfg = GameConfig()



    def __init__(self, args : ArgumentParser, config_overrides : dict = {}, MAX_MEMORY = 100_000, BATCH_SIZE = 1024, LR = 1e-5, seed=10):
        
        self.MAX_MEMORY = MAX_MEMORY
        self.BATCH_SIZE = BATCH_SIZE
        self.LR = LR
        
        self.log = getLogger(__name__)
        self.memory = deque(maxlen=MAX_MEMORY)
        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0.95
        self.record = 0
        self.pp_list = []
        self.stuck_start = float('inf')
        self._directions = [Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN]
        self.prev_pos = (Decimal('-1'), Decimal('-1'))
        self.prev_pos_int = (-1, -1)
        self.stat_display = self.get_stat_display()
        self._random = random.Random(seed)

        # Model + Trainer
        super().__init__(args, config_overrides)
        self.model = self.get_model(args)
        self.trainer = self.get_trainer(args)

    def get_model(self, args):
        input_size = self.__class__._get_input_layer_size(self.game_config)
        return Linear_QNet(input_size, 256, 4, load_model_path=args.load_model, save_model_path=args.save_model)
        
    def get_trainer(self, args) -> QTrainer:
        return QTrainer(self.model, lr=self.LR, gamma=self.gamma) 

    def prepare_env(self, state : GameState):
        from src.pacman.ghost_schedule import GhostSchedule
        from src.pacman.maze.objects import SpawnManager
        # Ustaw poziom 1 jako domyślny
        state.set_level(1, schedule=GhostSchedule(1))
        SpawnManager.spawn(Pacman(state=state))
        Blinky(state=state)
        Pinky(state=state)
        Inky(state=state)
        Clyde(state=state)
        self.maze_utils = MazeUtils(state)
        self.stat_display.maze_utils = self.maze_utils
        self.pp_list = []
        return state

    @staticmethod
    def _get_input_layer_size(game_config : GameConfig):

        vars = [
            (4 + 4 + 4 + 4 + 1 + 1 + 1),                # Informacje o duchach
            (1 + 4),                                # Informacje o energizerach
            1,                                      # Czas do zmiany stanu
            1,                                      # Czas do wygaśnięcia powerupa
            4,                                      # Nawigacja do najbliższego skrzyżowania
            4,                                      # Nawigacja do najbliższego punktu
            4                                       # Ściany
        ]

        return sum(vars)
    
    @staticmethod
    def _to_relative_pos(origin : Position, origin_direction : Direction, absolute : Position):
        relative = (0,0)
        if origin_direction == Direction.UP:
            relative = [
                absolute[0] - origin[0],
                absolute[1] - origin[1]

            ]
        elif origin_direction == Direction.DOWN:
            relative = [
                origin[0] - absolute[0],
                origin[1] - absolute[1]
            ]
        elif origin_direction == Direction.RIGHT:
            relative = [
                - origin[1] + absolute[1],
                - absolute[0] + origin[0]
            ]
        elif origin_direction == Direction.LEFT:
            relative = [
                origin[1] - absolute[1],
                absolute[0] - origin[0]

            ]
        return relative

    def _get_ghost_info(self, state : GameState) -> List:
        from src.pacman.actors import Ghost
        ghosts : List[Ghost] = [state.a_Blinky , state.a_Pinky, state.a_Inky, state.a_Clyde]
        arr = []
        mu = self.maze_utils
        pacman_pos = TO.to_int(state.a_Pacman.get_position())
        pacman_dir = state.a_Pacman.direction

        ghost_nav_a = [0] * 4
        ghost_nav_b = [0] * 4
        fright_nav = [0] * 4
        
        alive_count = 0


        # Wszystkie duchy mają taką samą wartość tych zmiennych
        is_chasing = ghosts[0].is_chasing
        is_scattered = not is_chasing
        spawn_point = ghosts[0].spawn_pos
        spawn_nav = mu.navigate_to_position(pacman_pos, spawn_point, pacman_dir)



        for ghost in ghosts:
            is_alive = not ghost.is_dead and ghost.is_spawned
            if is_alive: alive_count += 1

            pos = TO.to_int(ghost.get_position())
            if not is_alive: continue

            if not ghost.is_frightened:
                nav_a = [0] * 4
                nav_b = [0] * 4
                prev_block = ghost.history[-2]
                if prev_block != (-1, -1):
                    mu.graph.remove_edge(prev_block, pos)
                    nav_a = mu.navigate_to_position(pacman_pos, pos, pacman_dir)
                    # Teraz pozwól na cofnięcie się
                    mu.graph.add_edge(prev_block, pos)
                    nav_b = mu.navigate_to_position(pacman_pos, pos, pacman_dir)


                for i in range(4):
                    ghost_nav_a[i] = max(ghost_nav_a[i], nav_a[i])
                    ghost_nav_b[i] = max(ghost_nav_b[i], nav_b[i])
            else:
                # Tutaj to my pacman goni ducha - nie interesuje go to, czy może się w tym kierunku poruszyć
                nav = mu.navigate_to_position(pacman_pos, pos, pacman_dir)

                for i in range(4):
                    fright_nav[i] = max(nav[i], fright_nav[i])
            

        arr = [
            *ghost_nav_a,
            *ghost_nav_b,
            *fright_nav, 
            *spawn_nav,
            alive_count / 4,
            int(is_scattered),
            int(is_chasing)
        ]
        return arr
    
    @staticmethod 
    def _normalize_time(remaining : float):
        
        return 1/(remaining+1)

    @staticmethod
    def _time_to_state_change(state : GameState):
        schedule : GhostSchedule = state.schedule
        sched_timer = schedule._schedule_timer
        state_info = schedule.get_state_info(sched_timer)
        duration = state_info.end - state_info.start
        elapsed = sched_timer - state_info.start
        if duration <= 0: raise RuntimeError('Nieprawidłowy harmonogram duchów. Czas trwania stanu jest ujemny.')

        remaining = duration - elapsed
        if remaining < 0: remaining = 0

        
        return Player._normalize_time(remaining)
    
    def _get_powerpellet_info(self, state : GameState, mu : MazeUtils, intersection : Position) -> List:
        energizers = mu.get_energizers()
        working = sum([1 for e in energizers if not e.is_destroyed])
        workingp = working/len(energizers)

        nav = [0] * 4

        pacman = state.a_Pacman

        pacman_pos = pacman.get_position()
        pacman_dir = pacman.direction

        for energizer in energizers:
            pos = TO.to_int(energizer.get_position())
            nav2 = mu.navigate_to_position(pacman_pos, pos, pacman_dir)
            for i in range(len(nav2)):
                # Znajdź z największą wartością
                nav[i] = max(nav[i], nav2[i])

        return [
            workingp,
            *nav
        ]
    
    def _get_walls(self, maze : Maze, position : Position, origin_dir : Direction):
        walls = []
        for i in range(4):
            dir = self._directions[i]
            relative_to_origin = dir.remove_rotation(origin_dir)
            pos = maze.shift_position(position, relative_to_origin)
            walls.append(int(maze.check_wall(pos)))
        return walls

    def state_to_arr(self, state : GameState, mu : MazeUtils) -> List:
        from src.pacman.ghost_schedule import GhostSchedule
        maze : Maze = state.maze 
        position = TO.to_int(state.a_Pacman.get_position())

            
        return [
            *self._get_ghost_info(state),
            *self._get_powerpellet_info(state, mu, position),
            self._time_to_state_change(state),
            Player._normalize_time(state.remaining_powerup_time),
            *self.maze_utils.get_closest_dist_for_dirs(state, position, 'intersections'),
            *self.maze_utils.get_closest_dist_for_dirs(state, position),
            *self._get_walls(maze, position, state.a_Pacman.direction)
        ]        
    
    def can_make_a_decision(self, state : GameState):
        prev_pos = self.prev_pos

        new_pos = state.a_Pacman.get_precise_position()
        new_pos_int = state.a_Pacman.get_position()
        self.prev_pos = new_pos
        prev_pos_int = self.prev_pos_int
        self.prev_pos_int = new_pos_int
        
        is_stuck = prev_pos == new_pos

        if is_stuck:
            self.stuck_start = min(state.time_elapsed, self.stuck_start)
            stuck_duration = state.time_elapsed - self.stuck_start
            if stuck_duration >= self.cfg.STUCK_DURATION:
                self.log.info('Pacman utknął w miejscu - Dodatkowy stan decyzyjny')
                self.on_stuck(state)
                self.stuck_start = float('inf')
                return True
            else: return False
        elif state.is_game_over:
            self.log.info('Pacman osiągnął koniec gry - Dodatkowy stan decyzyjny końcowy')
            self.stuck_start = float('inf')
            self.on_game_over(state)
            return True
        elif prev_pos_int != new_pos_int:
            self.log.info('Pacman doszedł do skrzyżowania - Stan decyzyjny')
            self.stuck_start = float('inf')
            return True
        else:
            self.stuck_start = float('inf')
            return False
        
    def on_stuck(self, state):
        pass
    
    def on_game_over(self, state):
        pass

    def get_stat_display(self) -> StatsDisplay:
        """Zwraca instancję GameStatsDisplay"""
        return StatsDisplay()

    def getGame(self):
        return GameCore()

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        sample = None
        if len(self.memory) > self.BATCH_SIZE:
            sample = self._random.sample(self.memory, self.BATCH_SIZE)
        else:
            sample = self.memory

        states, actions, rewards, next_states, dones = zip(*sample)

        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def visit_state(self, state : GameState):
        maze : Maze = state.maze
        state_pp = self.state_to_arr(state, self.maze_utils)
        self.pp_list.append(state_pp)

    @abstractmethod
    def should_explore(self) -> bool:
        pass

    def make_decision(self, state : GameState):
        '''Metoda podejmuje decyzję na podstawie stanu gry.'''
        
        state_pp = self.pp_list[-1]

        if self.should_explore():
            move = self._random.choice(self._directions)
        else:
            state0 = torch.tensor(state_pp, dtype=torch.float)
            prediction = self.model.forward(state0)
            move_arr = torch.argmax(prediction).item()
            move : Direction = self._directions[move_arr]

        self.handle_events()
        return [move, True]

    
    def handle_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()

    def on_game_over(self, state):
        self.train_long_memory()

        if state.score >= self.record:
            self.record = state.score
            self.log.info(f'Nowy rekord: {self.record}')
            self.model.save()

    def action_to_arr(self, action : Direction):
        arr = [0,0,0,0]
        index = self._directions.index(action)
        arr[index] = 1
        return arr

    def on_move_made(self, old_state : GameState, new_state : GameState, player_move : Direction):
        # Oblicz nagrodę
        reward = new_state.score - old_state.score + new_state.ai_bonus - old_state.ai_bonus
        self.log.debug(f'Akcja: {player_move}, nagroda: {reward}')

        state_old_pp = self.pp_list[-2]
        state_new_pp = self.pp_list[-1]
        action_pp = self.action_to_arr(player_move)

        # Zapisz do pamięci krótkiej
        self.train_short_memory(state_old_pp, action_pp, reward, state_new_pp, new_state.is_game_over)

        # Pamiętaj
        self.remember(state_old_pp, action_pp, reward, state_new_pp, new_state.is_game_over)
        self.pp_list.pop(0)
        # Wyświetl wynik
        new_state.move_num = self.move_number
        self.stat_display.update(new_state)

    def on_update(self, state):
        self.maze_utils.update(state.a_Pacman.get_position())
        return super().on_update(state)