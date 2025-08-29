from functools import cached_property
from src.general.maze import Maze, MazeObject, Collidable
from src.pacman.actors import Actor, Ghost, Pacman
from src.general.direction import Direction
from abc import abstractmethod
from typing import Tuple, Dict
from logging import getLogger
from src.pacman.timer import start_time_timer
from collections import deque
from src.pacman.game_config import GameConfig
from src.pacman.game_state import GameState

class SpawnManager(MazeObject):
    """Klasa odpowiedzialna za zarządzanie odradzaniem pacmana i duchów w labiryncie.
    """

    def __init__(self, pos, state):
        """Inicjalizuje instancję klasy SpawnManager.
        
        :param pos: Pozycja, w której ma zostać zainicjalizowany SpawnManager.
        :type pos: tuple[int, int]
        """
        from src.pacman.game_core import GameCore

        self.spawn_pos = pos
        self._state : GameState = state
        super().__init__(pos, False)
        self.cfg = GameCore.get_main_instance().get_game_config()

    @cached_property
    def _maze(self):
        return self._state.maze


    @classmethod
    def spawn(cls, actor : Actor, now = False, first_time = True):
        """Spawnuje aktora w odpowiednim punkcie.
        :param actor: Aktor, który ma zostać zrespawnowany.
        :type actor: Actor
        """

        if isinstance(actor, Ghost):
            GhostSpawner.instance._spawn(actor, now, first_time)
        elif isinstance(actor, Pacman):
            PacmanSpawner.instance._spawn(actor, now)

    @staticmethod
    def get_spawn(actor : Actor):
        if isinstance(actor, Ghost):
            return GhostSpawner.instance._get_spawn()
        elif isinstance(actor, Pacman):
            return PacmanSpawner.instance._get_spawn()
    

    def _get_color(self):
        return None
    
    def _get_filled_ratio(self):
        return None

    def _get_named_layer(self):
        return 'map'
    
    @classmethod
    def _reload(cls):
        cls.instance = None

class PacmanSpawner(SpawnManager):
    """Klasa reprezentująca punkt odradzania Pacmana w labiryncie.
    Nie należy jej wywoływać do tworzenia Pacmana, do tego służy klasa SpawnManager.
    """
    def __init__(self, position, parent):
        PacmanSpawner.instance = self
        super().__init__(position, parent)

    def _get_spawn(self):
        return self.spawn_pos

    def draw(self):
        """Nic nie rysuj
        """
        pass
    
    def _spawn(self, obj : Actor, now : bool):
        obj.set_position(self.spawn_pos)
        obj.on_spawn()


class GhostSpawner(SpawnManager, Collidable):
    """Klasa reprezentująca punkt odradzania duchów w labiryncie.
    Nie należy jej wywoływać do tworzenia duchów, do tego służy klasa SpawnManager.
    """
    def __init__(self, position, parent):        
        self.spawn_queue = deque()
        self.prev_ghost = None
        GhostSpawner.instance = self
        super().__init__(position, parent)

    def _get_color(self):
        return None
    def _get_filled_ratio(self):
        return None
    def _get_named_layer(self):
        return 'map'
    
    def _get_spawn(self):
        return self.spawn_pos

    def _release_ghost(self, _):
        q = self.spawn_queue
        if len(q) == 0:
            return
        
        obj : Ghost = q.popleft()
        obj.set_position(self.spawn_pos)
        obj.on_leave_ghost_pen()
        self.prev_ghost = obj
 
    def _timer_wrapper(self):
        cfg = self.cfg
        start_time_timer(cfg.SPAWNG_EXIT_TIME, self._release_ghost, 4)


    def _spawn(self, obj : Actor, now : bool, first_time = True):
        obj : Ghost = obj
        q = self.spawn_queue

        pos = self.spawn_pos

        if not now:
            pos = self._maze.shift_position(pos, Direction.DOWN, 1)
            self.spawn_queue.append(obj)
        obj.set_position(pos)
        obj.direction = Direction.LEFT
        if first_time: obj.on_spawn()

        if now:
            obj.on_leave_ghost_pen()
        
        if not now and len(q) == 1:
            # W tym przypadku to manualnie wypuszczamy ducha
            self._timer_wrapper()


    
    def on_exit(self, obj):
        if id(self.prev_ghost) == id(obj):
            self.prev_ghost = None
            self._timer_wrapper()

    def on_enter(self, obj):
        if not isinstance(obj, Ghost):
            return
        ghost : Ghost = obj
        if ghost._is_dead:
            ghost._is_dead = False
            ghost._is_frightened = False
            ghost.is_spawned = False
            self._spawn(ghost, False, False)
            
    
MazeObject.character_to_class_mapping['P'] = PacmanSpawner
MazeObject.character_to_class_mapping['G'] = GhostSpawner

from src.general import reload_functions
def _reload():
    GhostSpawner._reload()
    PacmanSpawner._reload()
reload_functions.append(_reload)