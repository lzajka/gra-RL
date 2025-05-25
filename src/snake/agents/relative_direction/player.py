#!/usr/bin/env python3
from src.snake.agents.default.player import Player as defaultPlayer
from src.snake.agents.default.player import MAX_MEMORY, LR
from src.snake.agents.default.trainer import QTrainer
from src.snake.agents.default.model import Linear_QNet
from src.snake.game_core import GameCore
from src.snake.snake_dir import Direction
from src.snake.game_state import GameState
import random
import torch
from argparse import ArgumentParser
from src.snake.game_config import GameConfig
from collections import deque
from logging import getLogger
import numpy as np

class Player(defaultPlayer):
    def __init__(self, args : ArgumentParser, config_overrides : dict = {}):
        super().__init__(args, config_overrides)

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
        self.model = Linear_QNet(11, 256, 3, load_model_path=args.load_model, save_model_path=args.save_model)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    

    def detect_danger(self, state : GameState):
        """Nadpisana metoda detect_danger. Zwraca informację o zagrożeniu względem kierunku węża. Nie uwzględnia oczywistego zagrożenia z tyłu węża.
        :param state: Stan gry
        :type state: GameState
        :return: Tablica 0,1 zagrożeń względnych (lewo, prawo, przód)
        :rtype: list[int, int, int]
        """
        dangers = super().detect_danger(state)
        snake_dir = state.direction
        untrimmed_dangers = map_detection_array(snake_dir, dangers)
        return untrimmed_dangers[0:3]

    def detect_fruit(self, state : GameState):
        """Nadpisana metoda detect_fruit. Zwraca informację o owocu względem kierunku węża. Uwzględnia owoce znajdujące się z tyłu.

        :param state: Stan gry
        :type state: GameState
        :return: Tablica 0,1 owoców (lewo, prawo, przód, tył)
        :rtype: list[int, int, int, int]
        """
        fruits = super().detect_fruit(state)
        snake_dir = state.direction
        return map_detection_array(snake_dir, fruits)
    
    
    def state_to_arr(self, state : GameState):
        """Nadpisanie metody state_to_arr - dodaje absolutny kierunek węża.

        :param state: Aktualny stan gry
        :type state: GameState
        :return: Tablica 11 elementowa składająca się z tablic zwracanych przez `detect_danger`, `detect_fruit` oraz `get_absolute_direction`
        :rtype: List[int]*11
        """
        
        original = super().state_to_arr(state)
        return np.hstack([original, state.direction.get_dummies()])
    
    def action_to_arr(self, action):
        arr = super().action_to_arr(action)
        return arr[0:3]

    def make_decision(self, state : GameState):
        """Nadpisana metoda podejmująca decyzje na podstawie stanu gry. W tym przypadku dozwolone opcje, to - Lewo, Prawo, Przód.

        :param state: state
        :type state: GameState
        :return: Tablica w postaci [Wybrany kierunek, czy_gracz_wyszedł]
        :rtype: [Direction, boolean]
        """
        state_pp = self.state_to_arr(state)
        self.epsilon = 80 - self.round_number
        directions = [Direction.LEFT, Direction.RIGHT, Direction.UP]

        if random.randint(0, 200) < self.epsilon:
            move = random.choice(directions)
        else:
            state0 = torch.tensor(state_pp, dtype=torch.float)
            prediction = self.model.forward(state0)
            move_arr = torch.argmax(prediction).item()
            mapping = [Direction.LEFT, Direction.RIGHT, Direction.UP]
            move = mapping[move_arr]

        move = move.add_rotation(state.direction)
        self.handle_events(state.events)
        return [move, True]





def map_detection_array(snake_direction : Direction, arr):

    order = [
        Direction.LEFT,
        Direction.RIGHT,
        Direction.UP,
        Direction.DOWN
    ]
    mapping = {}
    for i in range(4):
        mapping[order[i]] = i

    ret = [-2]*4

    for i in range(4):
        object_dir = order[i]
        object_dir = object_dir.remove_rotation(snake_direction)

        ret[mapping[object_dir]] = arr[i]
    
    return ret