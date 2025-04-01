#!/usr/bin/env python3
from pygame.font import SysFont
class GameConfig:
    WINDOW_DIMENSION    = 1000
    TICKRATE_INITIAL    = 2
    TICKRATE_INCREASE   = 0.2
    TICKRATE_MAX        = 10
    BACKGROUND_COLOR    = 'black'
    SNAKE_COLOR         = 'cyan'
    FRUIT_COLOR         = 'red'
    DEATH_REWARD        = -10
    FRUIT_REWARD        = 10
    SURVIVAL_REWARD     = 0.1
    EDGES_KILL          = True
    CAPTION             = 'Snake'
    BOARD_SIZE          = 20

    SCORE_FONT_SIZE     = 36
    SCORE_FONT_COLOR    = 'white'
    SCORE_FONT          = None

    GAMEOVER_FONT_SIZE  = 72
    GAMEOVER_FONT_COLOR = 'red'
