from . import Ghost
from src.general.maze import Maze
from typing import Tuple

class Blinky(Ghost):
    """Reprezentuje ducha blinky w grze Pacman.
    """

    def __init__(self, *args, **kwargs):
        kwargs['name'] = 'blinky'
        Blinky.main_instance = self
        super().__init__(*args, **kwargs)
        
    @classmethod 
    def get_instance(cls):
        """Zwraca instancję ducha
        """
        return cls.main_instance



    def get_chase_position(self) -> Tuple[int, int]:
        """Zwraca pozycję chase dla ducha blinky.
        W przypadku blinky'ego jest to pozycja Pacmana.
        :return: Pozycja chase w postaci krotki (x, y).
        :rtype: Tuple[int, int]
        """
        from src.pacman.actors.pacman import Pacman
        pacman : Pacman = Pacman.get_instance()
        current_pos = pacman.get_position()

        return current_pos

    
    def copy(self):
        """Tworzy kopię ducha blinky."""
        return None
    
    def _get_color(self):
        from src.pacman.game_core import GameCore
        gc : GameCore = GameCore.get_main_instance()
        return gc.get_game_config().BLINKY_COLOR
    
    def on_powerup_activated(self):
        return super().on_powerup_activated()
    
    def on_powerup_deactivated(self):
        return super().on_powerup_deactivated()
    
    def get_csv_header():
        return ['BlinkyPosX', 'BlinkyPosY']
    def to_csv_line(self):
        pos = self.get_position()
        return [str(pos[0]), str(pos[1])]