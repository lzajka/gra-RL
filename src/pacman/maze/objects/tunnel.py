from src.general.maze import MazeObject, Collidable
from src.pacman.game_core import GameCore
from typing import Tuple
from .warp import Warp
from src.pacman.game_state import GameState
from src.pacman.actors import Actor, SpeedStatusEffect

class Tunnel(Collidable, MazeObject):
    """Obiekt oznaczający wejście/wyjście z tunelu.
    W zależnośći od tego, czy aktor wychodzi z tunelu może on spowolnić lub przywrócić oryginalną prędkość aktora.
    """

    touch_count = dict()
    
    def __init__(self, position, parent):
        super().__init__(position, parent)


    def _get_color(self):
        pass

    def copy(self):
        """Ponieważ ten obiekt się nie zmienia, można zwrócić self bez tworzenia kopii."""
        return self
    
    def _get_filled_ratio(self):
        return None
    
    def _get_named_layer(self):
        return 'map'

    
    def on_exit(self, obj):
        if not isinstance(obj, Actor): return
        a : Actor = obj

        if Tunnel.touch_count[a] % 2 == 1:
            a.clear_status_effect(SpeedStatusEffect.TUNNELING)

    def on_enter(self, obj):
        if not isinstance(obj, Actor): return
        a : Actor = obj

        if a not in Tunnel.touch_count:
            Tunnel.touch_count[a] = -1
        Tunnel.touch_count[a] += 1

        if Tunnel.touch_count[a] % 2 == 0:
            a.apply_speed_status_effect(SpeedStatusEffect.TUNNELING)

        


MazeObject.character_to_class_mapping['t'] = Tunnel