from src.general.direction import Direction
from . import Ghost
from src.general.maze import Maze
from typing import Tuple

class Pinky(Ghost):
    """Reprezentuje ducha Pinky w grze Pacman.
    """

    def __init__(self, *args, **kwargs):
        kwargs['name'] = 'pinky'
        super().__init__(*args, **kwargs)      
        Pinky.main_instance = self  

    @classmethod 
    def get_instance(cls):
        """Zwraca instancję ducha
        """
        return cls.main_instance
        

    def get_chase_position(self) -> Tuple[int, int]:
        """Zwraca pozycję chase dla ducha pinky.
        W przypadku pinky'ego jest to pozycja Pacmana przesunięta o 1 krok do przodu.

        :return: Pozycja chase w postaci krotki (x, y).
        :rtype: Tuple[int, int]
        """
        from src.pacman.actors.pacman import Pacman
        pacman : Pacman = Pacman.get_instance()
        current_pos = pacman.get_position()
        future_pos = current_pos
        for i in range(4):
            future_pos = Maze.shift_position(future_pos, pacman.direction)

        # Pinky jeżeli pacman idzie w górę to celuje w lewo
        if pacman.direction == Direction.UP:
            future_pos = (future_pos[0] - 4, future_pos[1])
        

        return future_pos

    
    def copy(self):
        """Tworzy kopię ducha pinky."""
        return None

    def _get_color(self):
        from src.pacman.game_core import GameCore
        gc : GameCore = GameCore.get_main_instance()
        return gc.get_game_config().PINKY_COLOR
    
    def on_powerup_activated(self):
        return super().on_powerup_activated()
    
    def on_powerup_deactivated(self):
        return super().on_powerup_deactivated()
    
    def get_csv_header():
        return ['PinkyPosX', 'PinkyPosY']
    def to_csv_line(self):
        pos = self.get_position()
        return [str(pos[0]), str(pos[1])]