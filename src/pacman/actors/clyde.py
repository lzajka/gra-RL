from src.general.direction import Direction
from . import Ghost
from src.general.maze import Maze

class Clyde(Ghost):
    """Reprezentuje ducha Clyde w grze Pacman.
    """

    def __init__(self, *args, **kwargs):
        kwargs['name'] = 'clyde'
        Clyde.main_instance = self
        super().__init__(*args, **kwargs)
        
    @classmethod 
    def get_instance(cls):
        """Zwraca instancję ducha
        """
        return cls.main_instance

    def get_chase_position(self):
        """Zwraca pozycję chase dla ducha Cylde."""
        from src.pacman.actors import Pacman, Blinky

        pacman : Pacman = Pacman.get_instance()

        # Najpierw policzy dystans Euklidesowy do Pacmana
        pacman_pos = pacman.get_position()
        clyde_pos = self.get_position()
        # W sumie nie ma sensu pierwiastkować, będę używał kwadratu dystansu
        distance = (pacman_pos[0] - clyde_pos[0]) ** 2 + (pacman_pos[1] - clyde_pos[1]) ** 2
        
        future_pos = None
        # Jeśli Pacman jest dalej niż 8 pól, to Clyde idzie do Pacmana, wykorzystam namierzanie blinky'ego
        if distance > 8 ** 2:
            future_pos = Blinky.get_instance().get_chase_position()
        # Jeśli Pacman jest bliżej, to Clyde idzie do swojej pozycji scatter
        else:
            future_pos = self.get_scatter_position()

        return future_pos
    
    def copy(self):
        """Tworzy kopię ducha Clyde'a."""
        return None
    
    def _get_color(self):
        from src.pacman.game_core import GameCore
        gc : GameCore = GameCore.get_main_instance()
        return gc.get_game_config().CLYDE_COLOR
    
    def on_powerup_activated(self):
        return super().on_powerup_activated()
    
    def on_powerup_deactivated(self):
        return super().on_powerup_deactivated()
    
    def get_csv_header():
        return ['ClydePosX', 'ClydePosY']
    def to_csv_line(self):
        pos = self.get_position()
        return [str(pos[0]), str(pos[1])]