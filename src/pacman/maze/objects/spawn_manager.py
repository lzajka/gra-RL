from src.general.maze import Maze, MazeObject, Collidable
from src.pacman.actors import Actor, Ghost, Pacman
from src.general.direction import Direction
from abc import abstractmethod
from typing import Tuple, Dict
from logging import getLogger
from src.pacman.timer import start_time_timer
from collections import deque
from src.pacman.game_config import GameConfig

class SpawnManager(MazeObject):
    """Klasa odpowiedzialna za zarządzanie odradzaniem pacmana i duchów w labiryncie.
    """

    def __init__(self, pos, parent):
        """Inicjalizuje instancję klasy SpawnManager.
        
        :param pos: Pozycja, w której ma zostać zainicjalizowany SpawnManager.
        :type pos: tuple[int, int]
        """
        super().__init__(pos, parent)
        from src.pacman.game_core import GameCore

        self.__class__.spawn_pos = pos
        self.__class__.maze = parent
        self.__class__.cfg = GameCore.get_main_instance().get_game_config()

    @classmethod
    def spawn(cls, actor : Actor, now = False, first_time = True):
        """Spawnuje aktora w odpowiednim punkcie.
        :param actor: Aktor, który ma zostać zrespawnowany.
        :type actor: Actor
        """

        if isinstance(actor, Ghost):
            GhostSpawner._spawn(actor, now, first_time)
        elif isinstance(actor, Pacman):
            PacmanSpawner._spawn(actor, now)

    @staticmethod
    def get_spawn(actor : Actor):
        if isinstance(actor, Ghost):
            return GhostSpawner._get_spawn()
        elif isinstance(actor, Pacman):
            return PacmanSpawner._get_spawn()
    

    def _get_color(self):
        return None
    
    def _get_filled_ratio(self):
        return None

    def _get_named_layer(self):
        return 'map'
    
    def copy(self):
        # W sumie to nas nie interesuje, czy się coś tutaj zmieni
        return []

class PacmanSpawner(SpawnManager):
    """Klasa reprezentująca punkt odradzania Pacmana w labiryncie.
    Nie należy jej wywoływać do tworzenia Pacmana, do tego służy klasa SpawnManager.
    """
    def __init__(self, position, parent):
        super().__init__(position, parent)

    @staticmethod
    def _get_spawn():
        return PacmanSpawner.spawn_pos

    def draw(self):
        """Nic nie rysuj
        """
        pass
    
    @staticmethod
    def _spawn(obj : Actor, now : bool):
        obj.set_position(PacmanSpawner.spawn_pos)
        obj.on_spawn()


class GhostSpawner(SpawnManager, Collidable):
    """Klasa reprezentująca punkt odradzania duchów w labiryncie.
    Nie należy jej wywoływać do tworzenia duchów, do tego służy klasa SpawnManager.
    """
    def __init__(self, position, parent):        
        GhostSpawner.spawn_queue = deque()
        GhostSpawner.prev_ghost = None
        super().__init__(position, parent)

    def _get_color(self):
        return None
    def _get_filled_ratio(self):
        return None
    def _get_named_layer(self):
        return 'map'
    
    @staticmethod
    def _get_spawn():
        return GhostSpawner.spawn_pos

    @staticmethod
    def _release_ghost(_):
        q = GhostSpawner.spawn_queue
        if len(q) == 0:
            return
        
        obj : Ghost = q.popleft()
        obj.set_position(GhostSpawner.spawn_pos)
        obj.on_leave_ghost_pen()
        GhostSpawner.prev_ghost = obj

    @staticmethod 
    def _timer_wrapper():
        cfg = GhostSpawner.cfg
        start_time_timer(cfg.SPAWNG_EXIT_TIME, GhostSpawner._release_ghost, 4)


    @staticmethod
    def _spawn(obj : Actor, now : bool, first_time = True):
        obj : Ghost = obj
        q = GhostSpawner.spawn_queue

        pos = GhostSpawner.spawn_pos

        if not now:
            pos = GhostSpawner.maze.shift_position(pos, Direction.DOWN, 1)
            GhostSpawner.spawn_queue.append(obj)
        obj.set_position(pos)
        obj.direction = Direction.LEFT
        if first_time: obj.on_spawn()

        if now:
            obj.on_leave_ghost_pen()
        
        if not now and len(q) == 1:
            # W tym przypadku to manualnie wypuszczamy ducha
            GhostSpawner._timer_wrapper()


    
    def on_exit(self, obj):
        if id(GhostSpawner.prev_ghost) == id(obj):
            GhostSpawner.prev_ghost = None
            GhostSpawner._timer_wrapper()

    def on_enter(self, obj):
        if not isinstance(obj, Ghost):
            return
        ghost : Ghost = obj
        if ghost._is_dead:
            ghost._is_dead = False
            ghost._is_frightened = False
            self._spawn(ghost, False, False)
            
    
MazeObject.character_to_class_mapping['P'] = PacmanSpawner
MazeObject.character_to_class_mapping['G'] = GhostSpawner