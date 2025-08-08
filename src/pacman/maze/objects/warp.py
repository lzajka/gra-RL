from src.general.maze import MazeObject, Collidable
from src.pacman.game_core import GameCore
from typing import Tuple

class Warp(Collidable, MazeObject):
    """Reprezentacja portalu w labiryncie Pacmana.
    Ponieważ przydatna będzie możliwość sprawdzania kolizji wykorzystam 
    """
    other_instance : 'Warp' = None
    disabled_for = set()

    def __init__(self, position, parent):
        """Inicjuje Warpa

        :param position: Określa punkt, w którym zaczyna się tunel
        :type position: Tuple[int, int]
        """
        self.teleport_position : Tuple[int, int] = None
        cfg = GameCore.get_main_instance().get_game_config()
        self.color = cfg.WARP_COLOR
        self.filled_ratio = cfg.WARP_FILLED_RATIO
        super().__init__(position, parent)
        
        if Warp.other_instance is not None:
            self._link_warp(Warp.other_instance)
            Warp.other_instance._link_warp(self)
        else:
            Warp.other_instance = self

    def _link_warp(self, other_warp : 'Warp'):
        """Podłącza warp z innym warpem. Metoda działa jednostronnie (na self).

        :param other_warp: Inny warp.
        :type other_warp: Warp
        """
        self.teleport_position = other_warp.get_position()

    def _get_color(self):
        return self.color

    def copy(self):
        """Ponieważ ten obiekt się nie zmienia, można zwrócić self bez tworzenia kopii."""
        return self
    
    def _get_filled_ratio(self):
        return self.filled_ratio
    
    def _get_named_layer(self):
        return 'map'

    
    def on_collision(self, obj):
        if obj in Warp.disabled_for:
            Warp.disabled_for.remove(obj)
            return
        
        from src.pacman.actors import Actor
        obj : Actor = obj
        # Chcę się upewnić, że pozycja to liczba całkowita
        if not (obj.position[0] % 1 == 0 and obj.position[1] % 1 == 0):
            return

 
        Warp.disabled_for.add(obj)
        obj.set_position(self.teleport_position)
        
    
MazeObject.character_to_class_mapping['W'] = Warp