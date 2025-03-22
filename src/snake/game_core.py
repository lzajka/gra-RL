#!/usr/bin/env python3

import pygame
from . import game_config as config

# pygame setup
pygame.init()
screen = pygame.display.set_mode(config.WINDOW_DIMMENSIONS)
clock = pygame.time.Clock()
running = True

screen.fill(color=config.BACKGROUND_COLOR)

while running:
    print('')

pygame.quit()