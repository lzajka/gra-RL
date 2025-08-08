from src.general.maze import MazeObject, Collidable
from src.pacman.game_core import GameCore
from typing import Tuple

class Tunnel(Collidable, MazeObject):
    """Obiekt oznaczający wejście/wyjście z tunelu.
    W zależnośći od tego, czy aktor wychodzi z tunelu może on spowolnić lub przywrócić oryginalną prędkość aktora.
    """

    def __init__(self, position, parent):
        pass


    def _get_color(self):
        return None

    def copy(self):
        """Ponieważ ten obiekt się nie zmienia, można zwrócić self bez tworzenia kopii."""
        return self
    
    def _get_filled_ratio(self):
        return None
    
    def _get_named_layer(self):
        return 'map'

    def draw(self):
        """Nic nie rysuj.
        """
        pass
    
    def on_collision(self, obj):
        from src.pacman.actors import Actor
        if isinstance(obj, Actor):
            actor : Actor = obj
            actor.toggle_tunnel()
    
MazeObject.character_to_class_mapping['t'] = Tunnel