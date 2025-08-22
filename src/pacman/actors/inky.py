from src.general.direction import Direction
from . import Ghost
from src.general.maze import Maze

class Inky(Ghost):
    """Reprezentuje ducha Inky w grze Pacman.
    """

    def __init__(self, **kwargs):
        kwargs['name'] = 'inky'
        super().__init__(**kwargs)

    def get_chase_position(self):
        """Zwraca pozycję chase dla ducha Inky."""
        from src.pacman.actors.pacman import Pacman
        from src.pacman.actors.blinky import Blinky
        pacman: Pacman = Pacman.get_instance(self._state)
        blinky : Blinky = Blinky.get_instance(self._state)

        if pacman.direction == Direction.UP:
            pacman_offset = self._maze.shift_position(pacman.get_position(), Direction.LEFT, 2)
            
        pacman_offset = self._maze.shift_position(pacman.get_position(), pacman.direction, 2)
        blinky_pos = blinky.get_position()
        offset = (blinky_pos[0] - pacman_offset[0], blinky_pos[1] - pacman_offset[1])
        future_pos = (pacman_offset[0] + offset[0] * 2, pacman_offset[1] + offset[1] * 2)

        return future_pos
    
    def _get_normal_color(self):
        from src.pacman.game_core import GameCore
        gc : GameCore = GameCore.get_main_instance()
        return gc.get_game_config().INKY_COLOR
    
    def on_powerup_activated(self):
        return super().on_powerup_activated()
    
    def on_powerup_deactivated(self):
        return super().on_powerup_deactivated()
    
    def get_csv_header():
        return ['InkyPosX', 'InkyPosY']
    def to_csv_line(self):
        pos = self.get_position()
        return [str(pos[0]), str(pos[1])]
    
    def _reset_rng(self):
        from random import Random
        self._rng = Random(self._game_config.INKY_FRNG)