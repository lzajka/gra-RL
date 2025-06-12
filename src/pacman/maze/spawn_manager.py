from .maze_object import MazeObject
from src.pacman.game_core import GameCore
from .maze import Maze
from src.pacman.actors.actor import Actor
from abc import abstractmethod
from typing import Tuple, Dict
from logging import getLogger

class SpawnManager(MazeObject):
    """Klasa odpowiedzialna za zarządzanie odradzaniem pacmana i duchów w labiryncie.
    """
    

    def __init__(self, pos):
        """Inicjalizuje instancję klasy SpawnManager.
        
        :param pos: Pozycja, w której ma zostać zainicjalizowany SpawnManager.
        :type pos: tuple[int, int]
        """
        super().__init__(pos)

    @classmethod
    def set_pacman_spawn(cls, spawn: Tuple[int, int]):
        """Ustawia punkt odradzania Pacmana.
        
        :param spawn: Punkt odradzania Pacmana w postaci krotki (x, y).
        :type spawn: tuple[int, int]
        """
        SpawnManager.pacman_spawn = spawn

    @classmethod
    def set_ghost_spawn(cls, spawn: Tuple[int, int]):
        """Ustawia punkt odradzania duchów.
        
        :param spawn: Punkt odradzania duchów w postaci krotki (x, y).
        :type spawn: tuple[int, int]
        """
        SpawnManager.ghost_spawn = spawn

    @classmethod
    def request_spawn(cls, actor : Actor):
        """Prosi o zrespawnowanie aktora w odpowiednim punkcie odradzania.
        :param actor: Aktor, który ma zostać zrespawnowany.
        :type actor: Actor
        """
        if not hasattr(cls, 'actor_hook_ids'):
            cls.actor_hook_ids = {}

        if actor in cls.actor_hook_ids:
            cls.log.debug('Nie można stworzyć kolejnej prośby dla tego samego aktora.')
            return
        func = lambda _ : cls._try_spawn(actor)
        cls.actor_hook_ids[actor] = GameCore.get_main_instance().register_frame_hook(func)


    @classmethod
    def _try_spawn(cls, actor : Actor):
        """Próbuje zrespawnować aktora w odpowiednim punkcie odradzania.
        :param actor: Aktor, który ma zostać zrespawnowany.
        :type actor: Actor
        """
        
        spawn_point = cls._get_spawn_point(actor)


        # Sprawdź pozycję gracza
        from src.pacman.actors.pacman import Pacman

        pacman : Pacman = Pacman.get_instance()
        pos = pacman.get_position()
        if pos == spawn_point:
            cls.log.info('Nie można zespawnować ducha - gracz blokuje spawn')
            return
        
        # Jeżeli tutaj jesteśmy, oznacza to, że udało się nam 
        hook_id = cls.actor_hook_ids[actor]
        GameCore.get_main_instance().unregister_frame_hook(hook_id)
        del cls.actor_hook_ids[actor]
        actor.set_position(spawn_point)
        actor.on_spawn()
        
    def _get_color(self):
        return None
    
    def _get_filled_ratio(self):
        return None
    
    @classmethod
    def _get_spawn_point(cls, actor: Actor) -> Tuple[int, int]:
        """Zwraca punkt odradzania dla danego aktora.
        :return: Punkt odradzania w postaci krotki (x, y).
        :rtype: tuple[int, int]
        """
        if actor.name == "Pacman":
            return cls.pacman_spawn
        elif actor.name == "Ghost":
            return cls.ghost_spawn
        else:
            raise ValueError("Nieznany typ aktora.")



    def _get_named_layer(self):
        return 'map'

    def to_csv_line(self):
        return [
            str(self.maze.pacman_spawn[0]),
            str(self.maze.pacman_spawn[1]),
            str(self.maze.ghost_spawn[0]),
            str(self.maze.ghost_spawn[1])
        ]

    def get_csv_header(self):
        return ['PacmanSpawnX', 'PacmanSpawnY', 'GhostSpawnX', 'GhostSpawnY']
    
    def copy(self):
        # W sumie to nas nie interesuje, czy się coś tutaj zmieni
        return [self.pacman_spawn, self.ghost_spawn]

class _PacmanSpawner(SpawnManager):
    """Klasa reprezentująca punkt odradzania Pacmana w labiryncie.
    Nie należy jej wywoływać do tworzenia Pacmana, do tego służy klasa SpawnManager.
    """
    def __init__(self, position):
        self.set_pacman_spawn(position)
    
    def draw(self):
        """Nic nie rysuj
        """
        pass
class _GhostSpawner(SpawnManager):
    """Klasa reprezentująca punkt odradzania duchów w labiryncie.
    Nie należy jej wywoływać do tworzenia duchów, do tego służy klasa SpawnManager.
    """
    def __init__(self, position):
        self.set_ghost_spawn(position)

    def _get_color(self):
        return GameCore.get_main_instance().get_game_config().GHOST_SPAWNER_COLOR
    def _get_filled_ratio(self):
        return GameCore.get_main_instance().get_game_config().GHOST_SPAWNER_FILLED_RATIO
    def _get_named_layer(self):
        return 'map'
    
MazeObject.character_to_class_mapping['P'] = _PacmanSpawner
MazeObject.character_to_class_mapping['G'] = _GhostSpawner