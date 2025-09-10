from collections import deque
from functools import cached_property
from src.general.utils.tuple_operations import TupleOperations as TO
from .actor import Actor
from .ghost_state import GhostState
from abc import ABC, abstractmethod
from src.general import Direction
from typing import *
from src.general.maze import MazeObject, Collidable, Maze
import array
from decimal import Decimal
from src.pacman import GameConfig
from src.pacman.actors.actor import Position
from random import Random
from src.pacman.timer import start_time_timer
from src.pacman.game_state import GameState
from src.general.utils import Transaction

class Ghost(Actor, Collidable):
    """Klasa implementująca aktora typu Ghost w grze pacman
    """

    ghosts : List['Ghost'] = []
    
    

    def __init__(self, state : GameState , respawn_interval: int = 0, name: str = "Ghost", is_copy = False, **kwargs):
        """Inicjalizuje aktora typu Ghost na podstawie punktu startowego i interwału respawnu.

        :param respawn_interval: Czas w sekundach po którym aktor zostanie zrespawnowany.
        :type respawn_interval: int
        :param name: Nazwa aktora.
        :type name: str
        """
        from src.pacman.game_core import GameCore
        self._gc = GameCore.get_main_instance()
        self._game_config : GameConfig = self._gc.get_game_config()
        self._is_chasing = False
        self._is_dead = False
        self.is_spawned = False
        self._rng : Random = None
        self.history = deque(maxlen=5)
        self.history.append((-1, -1))
        self.history.append((-1, -1))
        self.life_num = 0

        super().__init__(
            respawn_interval=respawn_interval, 
            name=name, 
            spawn=(1,0), # Ustawiam tak, aby obiekt później został przeniesiony do odpowiedniego miejsca. Tak, czy tak jest to w ścianie.
            base_speed=None,
            state=state,
            is_copy=is_copy
            ) 
        if not is_copy:
            Ghost.ghosts.append(self)
        from src.pacman.maze.objects import ScatterTarget
        

        self.scatter_pos = ScatterTarget.get_scatter_target(self.name)
        if self.scatter_pos is None:
            raise ValueError(f"Nie ustawiono pozycji scatter dla ducha {self.name}. Upewnij się, że jest zdefiniowana w pliku labiryntu")
    
    @property
    def is_chasing(self) -> bool:
        return self._is_chasing
    
    @is_chasing.setter
    def is_chasing(self, value: bool):
        if self._is_chasing == value:
            return
        self._is_chasing = value
        self.reverse_direction = True

    @is_chasing.deleter
    def is_chasing(self):
        del self._is_chasing
    

    @Actor.is_frightened.setter
    def is_frightened(self, value):
        changes_value = self._is_frightened != value
        if changes_value and value:
            # Odwróć kierunek
            self.reverse_direction = True
            # Zresetuj rng
            self._reset_rng()
        super(Ghost, self.__class__).is_frightened.fset(self, value)
    @property
    def is_dead(self) -> bool:
        return self._is_dead
    
    @is_dead.deleter
    def is_dead(self):
        del self._is_dead

    @abstractmethod
    def _reset_rng(self):
        pass
    
    def _get_speed_multiplier(self):
        level = self._state.level
        if self.is_dead: return Decimal('4.5')

        if level == 1:
            if self.is_frightened: return Decimal('0.50')
            elif self.is_tunneling: return Decimal('0.4')
            else: return Decimal('0.75')
        elif 2 <= level <= 4:
            if self.is_frightened: return Decimal('0.55')
            elif self.is_tunneling: return Decimal('0.45')
            else: return Decimal('0.85')
        elif 5 <= level <= 20:
            if self.is_frightened: return Decimal('0.60')
            elif self.is_tunneling: return Decimal('0.50')
            else: return Decimal('0.95')
        else:
            #if self.is_frightened: return None
            if self.is_tunneling: return Decimal('0.50')
            else: return Decimal('0.95')
        
        raise ValueError('Otrzymano nieznaną kombinację stan-poziom.')

    @classmethod
    def set_state_for_all(cls, is_chasing: bool = None, is_frightened: bool = None, is_dead: bool = None):
        """Ustawia stan pościgu dla wszystkich duchów.
        """
        for ghost in cls.ghosts:
            if is_chasing is not None: ghost.is_chasing = is_chasing
            if is_frightened is not None: ghost.is_frightened = is_frightened
            if is_dead is not None: ghost.is_dead = is_dead

    def get_scatter_position(self) -> Tuple[int, int]:
        """Zwraca pozycję scatter dla tego ducha.

        :return: Pozycja scatter w postaci krotki (x, y).
        :rtype: Tuple[int, int]
        """
        return self.scatter_pos
    
    @abstractmethod
    def get_chase_position(self) -> Tuple[int, int]:
        """Zwraca pozycję chase dla tego ducha.

        :return: Pozycja chase w postaci krotki (x, y).
        :rtype: Tuple[int, int]
        """
        pass
    
    def get_state(self) -> GhostState:
        """Zwraca aktualny stan ducha.

        :return: Stan ducha.
        :rtype: GhostState
        """
        if self.is_dead:
            return GhostState.EATEN
        elif self.is_frightened:
            return GhostState.FRIGHTENED
        elif self._is_chasing:
            return GhostState.CHASE
        else:
            return GhostState.SCATTER


    def _send_reversal_signal(self):
        """Sygnał do odwrócenia kierunku ruchu ducha.
        Odwrócenie występuje dopiero po wejściu na następny kwadrat
        """
        raise NotImplementedError("TODO")

    def get_frightened_position(self) -> Position:
        pos = self.get_position()
        next_pos = self._maze.shift_position(pos, self.direction)
        
        # sprawdź sąsiadów
        check_positions = [
            (next_pos[0], next_pos[1] - 1),  # UP
            (next_pos[0] - 1, next_pos[1]),  # LEFT
            (next_pos[0], next_pos[1] + 1),   # DOWN
            (next_pos[0] + 1, next_pos[1])  # RIGHT
        ]

        dirs = [Direction.UP, Direction.LEFT, Direction.DOWN, Direction.RIGHT]

        # Zabroń odwracanie kierunku
        check_positions[dirs.index(self.direction)] = (0,0)     # Ustawiam lokalizacje na ścianę.

        # Pomieszaj
        self._rng.shuffle(check_positions)

        for pos in check_positions:
            if not self._maze.check_wall(pos):
                return pos
            
        raise RuntimeError("Nie znaleziono dostępnej pozycji dla ducha w trybie FRIGHT. Sprawdź ściany i dostępność sąsiadów.")



    def get_target(self) -> Tuple[int, int]:
        """Zwraca cel, do którego duch ma się udać.
        Metoda może zwrócić pozycję do której duch nie może się udać.


        :return: Pozycja celu w postaci krotki (x, y).
        :rtype: Tuple[int, int]
        """
        from src.pacman.maze.objects import SpawnManager
        state = self.get_state()
        if state == GhostState.EATEN:
            return SpawnManager.get_spawn(self)
        elif state == GhostState.SCATTER:
            return self.get_scatter_position()
        elif state == GhostState.CHASE:
            return self.get_chase_position()
        elif state == GhostState.FRIGHTENED:
            return self.get_frightened_position()
    
    def _get_color(self):
        if self.is_frightened:
            return self._game_config.FRIGHT_COLOR
        else:
            return self._get_normal_color()
    
    @abstractmethod
    def _get_normal_color(self):
        pass

        
    def select_future_direction(self, commit : Transaction,  allow_turnbacks: bool = False):
        """Wybiera następny kierunek ruchu ducha
        """
        target_pos = self.get_target()

        # Przesuń pozycję ducha o 1 krok
        pos = self.get_position()
        next_pos = self._maze.shift_position(pos, commit.get_temp('direction'))

        
        # Teraz sprawdź, wszystkie kierunki wokół next_pos

        check_positions = [
            (next_pos[0], next_pos[1] - 1),  # UP
            (next_pos[0] - 1, next_pos[1]),  # LEFT
            (next_pos[0], next_pos[1] + 1),   # DOWN
            (next_pos[0] + 1, next_pos[1])  # RIGHT
        ]

        # Z wyjątkiem obecnej

        if not allow_turnbacks: check_positions[check_positions.index(pos)] = (999999999, 999999999)  # Ustaw na coś co nie jest możliwe

        # Uniemożliwiaj ściany
        for i in range(len(check_positions)):
            if self._maze.check_wall(check_positions[i]):
                check_positions[i] = (999999999, 999999999)


        # Sprawdź która bliżej manhatańsko do celu, priorytyzuj górę, ignoruj ściany

        dist = [
            (Direction.UP, abs(check_positions[0][0] - target_pos[0]) + abs(check_positions[0][1] - target_pos[1])),
            (Direction.LEFT, abs(check_positions[1][0] - target_pos[0]) + abs(check_positions[1][1] - target_pos[1])),
            (Direction.DOWN, abs(check_positions[2][0] - target_pos[0]) + abs(check_positions[2][1] - target_pos[1])),
            (Direction.RIGHT, abs(check_positions[3][0] - target_pos[0]) + abs(check_positions[3][1] - target_pos[1]))
        ]
        winner = [Direction.UP, 999999999] # Ustaw tak aby zawsze była lepsza opcja

        for direction, distance in dist:
            if distance < winner[1]:
                winner = [direction, distance]


        commit.write_temp('future_direction', winner[0])

    def commit_changes(self, current_state):
        ret = super().commit_changes(current_state)

        # Dodajemy, jeżeli nie jest martwy

        if not self.is_dead: self._add_to_history()

    def _add_to_history(self):
        pos = TO.to_int(self.get_position())
        prev_pos = self.history[-1]

        if pos != prev_pos:
            self.history.append(pos)

    def on_spawn(self):
        super().on_spawn()

        # Zrób tak aby duch decydował na pozycji spawnowej
        self.direction = Direction.LEFT

        self.history.clear()
        self.history.append((-1, -1))
        self.history.append((-1, -1))
        # Duch zazwyczaj idzie w lewo

        #spawn_pos = self.get_position()
        #self.set_position(Maze.shift_position(spawn_pos, Direction.LEFT))
        # Wykonaj select_future_direction, aby ustawić przyszły kierunek
        #self.select_future_direction(allow_turnbacks=True)
        # i od razu zmień kierunek na przyszły
        #self.direction = self.future_direction
        # Przywróć poprzednią pozycję
        #self.set_position(spawn_pos)
    
    def on_leave_ghost_pen(self):
        self._is_dead = False
        self.is_spawned = True
        self.direction = Direction.LEFT
        self.history.clear()
        self.history.append((-1, -1))
        spawn_pos = TO.to_int(self.get_position())
        self.history.append(spawn_pos)
        self.life_num = self.life_num + 1

    def kill(self):
        """Zabija ducha. Po zabiciu duch wraca na spawn.
        """
        from src.pacman.maze.objects import SpawnManager
        f = lambda _ : SpawnManager.spawn(self, False, False)
        reward = self._game_config.GHOST_EAT_REWARD
        self._state.score += reward
        self._is_dead = True
        current_life = self.life_num

        def spawn_return_timeout(_):
            if self.life_num == current_life:
                self.set_position(self.spawn_pos)
            
        
        start_time_timer(3, spawn_return_timeout, 4)

        
    def on_enter(self, obj):
        from src.pacman.actors.pacman import Pacman
        if not isinstance(obj, Pacman):
            return
        
        pacman : Pacman = obj
        state = self.get_state()
        if state == GhostState.FRIGHTENED:
            self.kill()
        elif state == GhostState.EATEN:
            return
        else:
            pacman.kill()

    def toggle_tunnel(self):
        self.in_tunnel = not self.in_tunnel

    @staticmethod
    def _reload1():
        Ghost.ghosts = []

    @cached_property
    def spawn_pos(self):
        from src.pacman.maze.objects import SpawnManager
        pos = SpawnManager.get_spawn(self)
        return TO.to_int(pos)

from src.general import reload_functions
def _reload():
    Ghost._reload1()
reload_functions.append(_reload)            