#!/usr/bin/env python3

from . import game_core
from . import game_config
from src.general.aplayer import APlayer
from src.general.direction import Direction as SnakeDir
from .game_state import GameState
import pygame
from argparse import ArgumentParser

class Player(APlayer):
    def getGame(self):
        return game_core.GameCore()

    def make_decision(self, state):
        events = state.events
        state_casted : GameState = state
        snake_controls = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]
        selected_dir = state_casted.direction
        for event in events:
            if event.type == pygame.KEYDOWN and event.key in snake_controls:
                selected_dir = SnakeDir(event.key)

            elif event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return [selected_dir, False]
            
        return [selected_dir, True]

