from functools import cached_property
from src.general.maze import MazeObject, Collidable
from src.pacman.actors import Actor

class Tunnel(Collidable, MazeObject):
    """Obiekt spowalniający duchy. Wypełnione są nim tunele.
    """

    touch_count = dict()
    
    def __init__(self, position, state, is_copy = False):
        self._state = state
        super().__init__(position, is_copy)



    def _get_color(self):
        pass
    
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
    
    @cached_property
    def _maze(self):
        return self._state.maze

        


MazeObject.character_to_class_mapping['t'] = Tunnel