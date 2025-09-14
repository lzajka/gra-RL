#!/usr/bin/env python3

from src.snake.game_core import GameCore
from src.snake.game_config import GameConfig
from src.general.aplayer import APlayer
from .model import Linear_QNet
from .trainer import QTrainer

import pygame
import torch
import random
import numpy as np
from collections import deque
from logging import getLogger
import gymnasium as gym

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


    def make_decision(self, state):
        '''Metoda podejmuje decyzję na podstawie stanu gry.'''
        state_pp = self.state_to_arr(state)
        self.epsilon = 80 - self.round_number

    
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


        # Zapisz do pamięci krótkiej
        #self.train_short_memory(state_old_pp, action_pp, reward, state_new_pp, new_state.is_game_over)

        # Pamiętaj
        #self.remember(state_old_pp, action_pp, reward, state_new_pp, new_state.is_game_over)

        # Wyświetl wynik
        #self.stat_display.update(new_state)