from src.general.maze import MazeObject, Collidable
from src.pacman.game_config import GameConfig

class Point(MazeObject, Collidable):
    """Reprezentuje punktu w labiryncie Pacmana.
    Ściana jest obiektem statycznym, który nie zmienia swojej pozycji ani stanu w trakcie gry.
    """

    def __init__(self, position: tuple[int, int], parent):
        """Inicjalizuje obiekt ściany na podstawie jego pozycji.

        :param position: Pozycja ściany w labiryncie w postaci krotki (x, y).
        :type position: tuple[int, int]
        """
        super().__init__(position, parent)
    
    def _draw(self):
        """Metoda zwracająca reprezentację obiektu w formie graficznej."""
        
        pass

    def to_csv_line():
        return []
    def get_csv_header():
        return []
    
    def _get_color(self):
        return GameConfig.POINT_COLOR
    
    def _get_filled_ratio(self):
        return GameConfig.POINT_FILLED_RATIO
    
    def _get_named_layer(self):
        return 'map'
    
    def copy(self):
        s = Point(self.position)
        return s
    
    def get_reward(self):
        return 1
    
    def get_point_type(self):
        return 'point'

    def on_enter(self, obj):
        from src.pacman.actors.pacman import Pacman
        from src.pacman.game_state import GameState
        gs = GameState.get_main_instance()

        if not isinstance(obj, Pacman):
            return

        pacman : Pacman = obj

        self.prev_multi = pacman.get_speed_multiplier()
        gs.score += self.get_reward()
        gs.collected[self.get_point_type()] += 1
        pacman.pause(1)
        self.destroy()

            


MazeObject.character_to_class_mapping['.'] = Point