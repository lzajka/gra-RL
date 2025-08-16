from src.general.maze import MazeObject, Collidable
from src.pacman.actors import Actor

class Tunnel(Collidable, MazeObject):
    """Obiekt spowalniający duchy. Wypełnione są nim tunele.
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
        a.is_tunneling = False

    def on_enter(self, obj):
        if not isinstance(obj, Actor): return
        a : Actor = obj
        a.is_tunneling = True

        


MazeObject.character_to_class_mapping['t'] = Tunnel