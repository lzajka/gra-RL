#!/usr/bin/env python3

from src.snake.game_core import GameCore
from src.snake.game_config import GameConfig
from src.general.aplayer import APlayer
from src.snake.snake_dir import Direction as SnakeDir
from src.snake.game_state import GameState
from .model import Linear_QNet
from .trainer import QTrainer

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

        super().__init__(GameCore(), args, config_overrides)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self, state, action, reward, next_state, done):
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
        move = [SnakeDir.LEFT, SnakeDir.RIGHT, SnakeDir.UP, SnakeDir.DOWN]
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
            SnakeDir.LEFT: 0,
            SnakeDir.RIGHT: 1,
            SnakeDir.UP: 2,
            SnakeDir.DOWN: 3
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
        pass



    def make_decision2(self, state_pp):
        '''Metoda podejmuje decyzję na podstawie stanu gry.'''
        self.epsilon = 80 - self.n_games
        directions = [SnakeDir.LEFT, SnakeDir.RIGHT, SnakeDir.UP, SnakeDir.DOWN]

        if random.randint(0, 200) < self.epsilon:
            move = random.choice(directions)
        else:
            state0 = torch.tensor(state_pp, dtype=torch.float)
            prediction = self.model.forward(state0)
            move_arr = torch.argmax(prediction).item()
            mapping = [SnakeDir.LEFT, SnakeDir.RIGHT, SnakeDir.UP, SnakeDir.DOWN]
            move = mapping[move_arr]
        return move
    
    def handle_events(self, event):
        for event in event:
            if event.type == pygame.QUIT:
                self.game.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.quit()

    # Jednak tutaj trzeba to override'ować
    def play(self, config = None):
        scores = []
        mean_scores = []
        current_score = 0
        record = -10
        is_running = True
        while is_running:
            state = self.game.restart(config)
            old_score = state.score
            state_old_pp = self.state_to_arr(state)
            reward = 0

            while not state.is_game_over and is_running:
                # Wykonaj ruch
                action = self.make_decision2(state_old_pp)
                action_pp = self.action_to_arr(action)

                # Zapisz stan
                state = self.game.make_move(action)
                self.handle_events(state.events)


                state_new_pp = self.state_to_arr(state)

                # Oblicz nagrodę
                current_score = state.score
                reward = current_score - old_score

                # Zapisz do pamięci krótkiej
                self.train_short_memory(state_old_pp, action_pp, reward, state_new_pp, state.is_game_over)

                # Pamiętaj
                self.remember(state_old_pp, action_pp, reward, state_new_pp, state.is_game_over)

                if state.is_game_over:
                    # Jeśli gra się zakończyła, zapisz do pamięci długiej
                    self.n_games += 1
                    self.train_long_memory(state_old_pp, action_pp, reward, state_new_pp, state.is_game_over)

                    if current_score > record:
                        record = current_score
                        self.model.save()

                    self.log.info(f'Gra: {self.n_games}, wynik: {current_score}, rekord: {record}')

                # Ustaw state_new jako state_old
                old_score = current_score
                state_old_pp = state_new_pp.copy()