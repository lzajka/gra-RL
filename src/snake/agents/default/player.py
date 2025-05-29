#!/usr/bin/env python3

from src.snake.game_core import GameCore
from src.snake.game_config import GameConfig
from src.general.aplayer import APlayer
from general.direction import Direction
from src.snake.game_state import GameState
from .model import Linear_QNet
from .trainer import QTrainer
from src.snake.game_stats_display import GameStatsDisplay

import pygame
import torch
import random
import numpy as np
from collections import deque
from logging import getLogger

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001
from argparse import ArgumentParser
class Player(APlayer):

    cfg = GameConfig()



    def __init__(self, args : ArgumentParser, config_overrides : dict = {}):
        self.log = getLogger(__name__)
        GameConfig.TICKRATE_INITIAL = 1000
        GameConfig.TICKRATE_INCREASE = 0
        GameConfig.TICKRATE_MAX = 1000
        self.memory = deque(maxlen=MAX_MEMORY)
        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0.99
        self.record = 0
        # Model + Trainer
        self.model = Linear_QNet(8, 256, 4, load_model_path=args.load_model, save_model_path=args.save_model)
        
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        super().__init__(args, config_overrides)
        self.stat_display = self.get_stat_display()

    def get_stat_display(self) -> GameStatsDisplay:
        """Zwraca instancję GameStatsDisplay"""
        return GameStatsDisplay()

    def getGame(self):
        return GameCore()

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        sample = None
        if len(self.memory) > BATCH_SIZE:
            sample = random.sample(self.memory, BATCH_SIZE)
        else:
            sample = self.memory

        states, actions, rewards, next_states, dones = zip(*sample)

        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def detect_danger(self, state : GameState):
        '''Sprawdź czy wąż jest w niebezpieczeństwie'''
        [snake_x, snake_y] = state.snake_position
        neighbors = [(snake_x - 1, snake_y), (snake_x + 1, snake_y), (snake_x, snake_y - 1), (snake_x, snake_y + 1)]
        move = [Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN]
        prev_move = state.direction

        game : GameCore = self.game

        danger = [
            game.check_death(prev_move, move[0], neighbors[0]), # l
            game.check_death(prev_move, move[1], neighbors[1]), # r
            game.check_death(prev_move, move[2], neighbors[2]), # u
            game.check_death(prev_move, move[3], neighbors[3]), # d
        ]

        for i in range(len(danger)):
            if danger[i]:
                 self.log.debug(f'Niebezpieczeństwo w kierunku: {move[i]}')
    
        return danger

    def detect_fruit(self, state):
        snake_x, snake_y = state.snake_position
        fruit_x, fruit_y = state.fruit_position
        return [
            fruit_x < snake_x, # l
            fruit_x > snake_x, # r
            fruit_y < snake_y, # u
            fruit_y > snake_y# d
        ]

    def action_to_arr(self, action):
        '''Metoda przygotowuje akcję do przetworzenia przez sieć neuronową'''
        mapping = {
            Direction.LEFT: 0,
            Direction.RIGHT: 1,
            Direction.UP: 2,
            Direction.DOWN: 3
        }

        arr = [0, 0, 0, 0]
        arr[mapping[action]] = 1
        return arr
    


    def state_to_arr(self, state : GameState):
        '''Metoda przygotowuje stan gry do przetworzenia przez sieć neuronową'''

        #direction = self.action_to_arr(state.direction)
        state_arr = self.detect_danger(state) + self.detect_fruit(state)
        return np.array(state_arr, dtype=np.int32)

    def make_decision(self, state):
        '''Metoda podejmuje decyzję na podstawie stanu gry.'''
        state_pp = self.state_to_arr(state)
        self.epsilon = 80 - self.round_number
        directions = [Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN]

        if random.randint(0, 200) < self.epsilon:
            move = random.choice(directions)
        else:
            state0 = torch.tensor(state_pp, dtype=torch.float)
            prediction = self.model.forward(state0)
            move_arr = torch.argmax(prediction).item()
            mapping = [Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN]
            move = mapping[move_arr]

        self.handle_events(state.events)
        return [move, True]

    
    def handle_events(self, event):
        for event in event:
            if event.type == pygame.QUIT:
                self.game.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.quit()

    def on_decision_made(self, state, player_move):
        pass

    def on_game_over(self, state):
        if state.score > self.record:
            self.record = state.score
            self.log.info(f'Nowy rekord: {self.record}')
            self.model.save()
        

    def on_move_made(self, old_state, new_state, player_move):

        # Oblicz nagrodę
        reward = new_state.score - old_state.score
        self.log.debug(f'Akcja: {player_move}, nagroda: {reward}')

        state_old_pp = self.state_to_arr(old_state)
        state_new_pp = self.state_to_arr(new_state)
        action_pp = self.action_to_arr(player_move)

        # Zapisz do pamięci krótkiej
        self.train_short_memory(state_old_pp, action_pp, reward, state_new_pp, new_state.is_game_over)

        # Pamiętaj
        self.remember(state_old_pp, action_pp, reward, state_new_pp, new_state.is_game_over)

        # Wyświetl wynik
        self.stat_display.update(new_state)