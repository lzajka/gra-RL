from pygame.font import SysFont
from decimal import Decimal
class GameConfig:
    WINDOW_DIMENSION    = (700, 775)
    TICKRATE_INITIAL    = 2
    TICKRATE_INCREASE   = 0.2
    TICKRATE_MAX        = 10
    MAZE_FILE           = "src/pacman/maze/mazes/1.txt"
    STARTING_LIVES      = 3

    DEATH_REWARD        = -10
    FRUIT_REWARD        = 10
    GHOST_EAT_REWARD    = 100
    SURVIVAL_REWARD     = 0
    EDGES_KILL          = True
    CAPTION             = 'Pacman'


    SCORE_FONT_SIZE     = 36
    SCORE_FONT_COLOR    = 'white'
    SCORE_FONT          = None

    GAMEOVER_FONT_SIZE  = 72
    GAMEOVER_FONT_COLOR = 'red'

    WALL_COLOR          = 'blue'
    WALL_FILLED_RATIO   = 1
    PACMAN_COLOR        = 'yellow'
    ACTOR_FILLED_RATIO  = 0.8
    INKY_COLOR          = 'blue'
    PINKY_COLOR         = 'pink'
    BLINKY_COLOR        = 'red'
    CLYDE_COLOR         = 'cyan'
    FRIGHT_COLOR        = 'purple'
    ENERGIZER_COLOR     = 'green'
    ENERGIZER_FILLED_RATIO = 0.5
    ENERGIZER_REWARD    = 50
    GHOST_SPAWNER_COLOR = 'grey'
    GHOST_SPAWNER_FILLED_RATIO = 1
    PINKY_FRNG          = 151
    BLINKY_FRNG         = 519
    INKY_FRNG           = 678
    CLYDE_FRNG          = 712
    SPAWNG_EXIT_TIME    = 1
    GHOST_SPAWN_RETURN_T= 4
    POINT_COLOR         = 'white'
    POINT_FILLED_RATIO  = 0.2
    POINT_REWARD        = 10
    FRUIT_COLOR         = 'green'
    FRUIT_FILLED_RATIO  = 0.5
    WARP_COLOR          = 'lightblue'
    WARP_FILLED_RATIO   = 1
    BASE_SPEED          = Decimal('0.1')
