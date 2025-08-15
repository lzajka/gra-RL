from .tunnel import Tunnel
from src.general.maze import MazeObject
from src.pacman.game_core import GameCore
from src.general.maze import PrecisePosition
from src.general.utils.tuple_operations import TupleOperations

class Warp(Tunnel):
    """Reprezentacja portalu w labiryncie Pacmana.
    Ponieważ przydatna będzie możliwość sprawdzania kolizji wykorzystam 
    """
    other_instance : 'Warp' = None
    just_teleported = set()

    def __init__(self, position, parent):
        """Inicjuje Warpa

        :param position: Określa punkt, w którym zaczyna się tunel
        :type position: Tuple[int, int]
        """
        self.teleport_offset : PrecisePosition = None
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
        other = other_warp.get_precise_position()
        me = self.get_precise_position()
        self.teleport_offset = TupleOperations.subtract_tuples(other, me)

    def _get_color(self):
        return self.color

    def copy(self):
        """Ponieważ ten obiekt się nie zmienia, można zwrócić self bez tworzenia kopii."""
        return self
    
    def _get_filled_ratio(self):
        return self.filled_ratio
    
    def _get_named_layer(self):
        return 'map'
    

    def on_enter(self, obj):        
        super().on_enter(obj)
        from src.pacman.actors import Actor
        obj : Actor = obj
        # Chcę się upewnić, że pozycja to liczba całkowita
        if obj not in Warp.just_teleported:
            Warp.just_teleported.add(obj)
            new_pos = obj.get_precise_position()
            new_pos = TupleOperations.add_tuples(new_pos, self.teleport_offset)
            obj.set_position(new_pos)
        else:
            Warp.just_teleported.remove(obj)
        
    
MazeObject.character_to_class_mapping['W'] = Warp