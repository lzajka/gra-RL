from src.general.direction import Direction
from . import Ghost
from src.pacman.maze import Maze

class Inky(Ghost):
    """Reprezentuje ducha Inky w grze Pacman.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "Inky"
        Maze.get_main_instance().inky = self

    def get_scatter_position(self):
        """Zwraca pozycję scatter dla ducha Inky."""
        return None
        

    def get_chase_position(self):
        """Zwraca pozycję chase dla ducha Inky."""
        from src.pacman.actors.pacman import Pacman
        from src.pacman.actors.blinky import Blinky
        pacman: Pacman = Pacman.get_instance()
        blinky : Blinky = Blinky.get_instance()

        if pacman.direction == Direction.UP:
            pacman_offset = Maze.shift_position(pacman.get_position(), Direction.LEFT, 2)
            
        pacman_offset = Maze.shift_position(pacman.get_position(), pacman.direction, 2)
        blinky_pos = blinky.get_position()
        offset = (blinky_pos[0] - pacman_offset[0], blinky_pos[1] - pacman_offset[1])
        future_pos = (pacman_offset[0] + offset[0] * 2, pacman_offset[1] + offset[1] * 2)

        return future_pos
    
    def copy(self):
        """Tworzy kopię ducha Inky."""
        return None
    
    
    @classmethod
    def get_instance(cls):
        """Zwraca instancję Inky'ego.
        
        :return: Instancja Inky'ego.
        :rtype: Inky
        """
        from src.pacman.maze import Maze
        return Maze.get_main_instance().inky
    
    def _get_color(self):
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