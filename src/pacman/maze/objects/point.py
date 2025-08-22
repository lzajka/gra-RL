from functools import cached_property
from src.general.maze import MazeObject, Collidable
from src.pacman.game_config import GameConfig

class Point(MazeObject, Collidable):
    """Reprezentuje punktu w labiryncie Pacmana.
    Ściana jest obiektem statycznym, który nie zmienia swojej pozycji ani stanu w trakcie gry.
    """

    def __init__(self, position: tuple[int, int], state, is_copy = False):
        """Inicjalizuje obiekt ściany na podstawie jego pozycji.

        :param position: Pozycja ściany w labiryncie w postaci krotki (x, y).
        :type position: tuple[int, int]
        """
        from src.pacman.game_core import GameCore
        from src.pacman import GameConfig
        from src.pacman.game_state import GameState
        game = GameCore.get_main_instance()
        self.cfg = game.get_game_config()

        self._state : GameState = state
        self._state.max_points += 1
        super().__init__(position, is_copy)
    
    @cached_property
    def _maze(self):
        return self._state.maze
    
    def _draw(self):
        """Metoda zwracająca reprezentację obiektu w formie graficznej."""
        
        pass

    def to_csv_line():
        return []
    def get_csv_header():
        return []
    
    def _get_color(self):
        return self.cfg.POINT_COLOR
    
    def _get_filled_ratio(self):
        return self.cfg.POINT_FILLED_RATIO
    
    def _get_named_layer(self):
        return 'map'
    
    def copy(self, state):
        s = Point(self.position, state, is_copy=True)
        return s
    
    def get_reward(self):
        return self.cfg.POINT_REWARD
    
    def get_point_type(self):
        return 'point'
    
    def _eat_length(self):
        return 1
    
    def _check_if_all_collected(self):
        """Metoda sprawdza czy wszystkie zbieralne punkty zostały zebrane.
        """
        collected = self._state.collected
        max_points = self._state.max_points

        if sum(collected.values()) == max_points:
            self._state.is_game_over = True
            self._state.score += self.cfg.WIN_REWARD

    def on_enter(self, obj):
        from src.pacman.actors.pacman import Pacman
        from src.pacman.game_state import GameState

        if not isinstance(obj, Pacman):
            return

        pacman : Pacman = obj

        self._state.score += self.get_reward()
        self._state.collected[self.get_point_type()] += 1
        self._check_if_all_collected()
        pacman.pause(self._eat_length())
        self.destroy()

            


MazeObject.character_to_class_mapping['.'] = Point