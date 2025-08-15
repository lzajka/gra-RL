from .point import Point
from src.general.maze import MazeObject
from src.pacman.actors import Pacman, Ghost, GhostState
from src.pacman.game_state import GameState


class Energizer(Point):
    def __init__(self, position: tuple[int, int], parent):
        """Inicjalizuje obiekt na podstawie jego pozycji.

        :param position: Pozycja w labiryncie w postaci krotki (x, y).
        :type position: tuple[int, int]
        """
        from src.pacman.game_core import GameCore
        self.gc = GameCore.get_main_instance()
        self.cfg = self.gc.get_game_config()
        super().__init__(position, parent)

    def get_point_type(self):
        return 'energizer'
    
    def get_reward(self):
        return self.cfg.ENERGIZER_REWARD
    
    def _get_color(self):
        return self.cfg.ENERGIZER_COLOR
    
    def _get_filled_ratio(self):
        return self.cfg.ENERGIZER_FILLED_RATIO
    
    def _eat_length(self):
        return 3
    
    def copy(self):
        return Energizer(self.position, self.maze)

    def on_enter(self, obj):
        super().on_enter(obj)
        if not isinstance(obj, Pacman):
            return
        self.activate()

    def _get_duration(self, level):
        arr = [6,5,4,3,2,5,2,2,1,5,2,1,1,3,1,1,0,1,0,0,0]
        if level >= 21:
            return arr[-1]
        return arr[level]

    
    def activate(self):
        from src.pacman.timer import start_time_timer
        pac = Pacman.get_instance()
        pac.apply_speed_status_effect(GhostState.FRIGHTENED)
        Ghost.set_state_for_all(is_frightened=True)
        self.gc._ghost_schedule.is_timer_paused = True
        lvl = self.gc.get_current_state().level
        start_time_timer(self._get_duration(lvl), self.deactivate)
    
    def deactivate(self, GameState : GameState):
        pac = Pacman.get_instance()
        pac.clear_status_effect(GhostState.FRIGHTENED)
        Ghost.set_state_for_all(is_frightened=False)
        self.gc._ghost_schedule.is_timer_paused = False

        
        
    

MazeObject.character_to_class_mapping['e'] = Energizer