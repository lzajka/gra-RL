from functools import cached_property
from typing import *
from src.general.maze import MazeObject, Collidable, Maze
from abc import ABC, abstractmethod
from src.general import Direction
from src.pacman.game_core import GameCore, GameState
from collections import deque
from decimal import Decimal, ROUND_DOWN
from src.general.utils import TupleOperations
from src.general.maze import PrecisePosition, Position
from src.general.utils import Transaction
detected_collisions = set()
detected_last_time = set()

def execute_on_collisions(_):
    global detected_collisions, detected_last_time

    # Sprawdź które wyszły z kolizji
    exited = detected_last_time - detected_collisions
    entered = detected_collisions - detected_last_time

    for c in exited:
        collision : Tuple['Actor', Collidable] = c
        actor, collidable = collision
        collidable.on_exit(actor)
    
    for c in entered:
        collision : Tuple['Actor', Collidable] = c
        actor, collidable = collision
        collidable.on_enter(actor)
    
    for c in detected_collisions:
        collision : Tuple['Actor', Collidable] = c
        actor, collidable = collision
        collidable.on_continue(actor)

    detected_last_time = detected_collisions.copy()
    detected_collisions.clear()
    

class Actor(MazeObject):
    """Klasa reprezentująca aktora w grze Pacman, dziedzicząca po MazeObject.
    Aktorzy mogą poruszać się po labiryncie i posiadają stan.
    """
    registered_collision_hooks = False
    _all_subs : List['Actor'] = []

    @staticmethod
    def _reload_all():
        Actor.registered_collision_hooks = False
        for s in Actor._all_subs:
            s._reload()
        Actor._all_subs = []
    
    @classmethod
    def _reload(cls):
        # To jest wywoływane jedynie w kontekście obecnej instancji, więc tak może zostać
        state = GameCore.get_main_instance().get_current_state()
        setattr(state, f'a_{cls.__name__}', None)

    def __init__(self, respawn_interval: int = 0, name: str = "Actor", spawn: Tuple[int, int] = None, base_speed=None, state : GameState = None, is_copy = False):
        """Inicjalizuje aktora na podstawie punktu startowego i interwału respawnu.

        :param Maze maze: Obiekt labiryntu, w którym aktor będzie się poruszał.
        :type maze: Maze
        :param respawn_interval: Czas w sekundach po którym aktor zostanie zrespawnowany.
        :type respawn_interval: int
        :param name: Nazwa aktora.
        :type name: str
        :param spawn: Punkt startowy aktora w labiryncie.
        :type spawn: Tuple[int, int]
        """
        game : GameCore = GameCore.get_main_instance()
        config = game.get_game_config()
        if not Actor.registered_collision_hooks and not is_copy:
            
            game.register_frame_hook(execute_on_collisions, priority_group=4)
            Actor.registered_collision_hooks = True

        if base_speed is None:
            base_speed = config.BASE_SPEED

        self.new_pos = 0
        self._is_frightened = False
        self.respawn_interval = respawn_interval
        self.name = name
        self.direction = Direction.RIGHT
        self._base_speed = base_speed
        self._pause = 0
        self._prev_block = (Decimal(-1), Decimal(-1))       
        self.status_effects = dict()
        self.reverse_direction = False
        self._state = state
        self._level = state.level
        self._is_tunneling = False
        self.future_direction = None
        setattr(state, f'a_{self.__class__.__name__}', self)

        if not is_copy:
            Actor._all_subs.append(self)

        super().__init__(spawn, is_copy, is_static=False)

    @cached_property
    def _maze(self) -> Maze:
        return self._state.maze


    def copy(self, state = None):
        """Tworzy kopię aktora. Nie wszystkie elementy są kopiowane - elementy niezmienne, takie jak ściany nie są kopiowane.

        :return: Kopia aktora.
        :rtype: Actor
        """
        if state is None:
            raise ValueError("Aktor musi być skopiowany do labiryntu.")
        
        actor_copy = self.__class__(
            respawn_interval = self.respawn_interval, 
            name = self.name, 
            spawn = self.position,              # spawn jest używany jedynie do przypisania pozycji
            base_speed = self._base_speed,
            state = state,
            is_copy = True
            )
        
        actor_copy.direction = self.direction
        actor_copy._prev_block = self._prev_block
        actor_copy._pause = self._pause
        actor_copy.reverse_direction = self.reverse_direction
        actor_copy._is_tunneling = self._is_tunneling
        actor_copy._is_frightened = self._is_frightened
        actor_copy._level = self._level
        return actor_copy
        

    @property
    def is_tunneling(self):
        return self._is_tunneling
    
    @is_tunneling.setter
    def is_tunneling(self, value):
        self._is_tunneling = value

    @property
    def is_frightened(self) -> bool:
        return self._is_frightened
    
    @is_frightened.setter
    def is_frightened(self, value: bool):
        self._is_frightened = value

    @abstractmethod
    def _get_speed_multiplier(self):
        pass

    @property
    def multiplier(self):
        value = self._get_speed_multiplier()
        if self._base_speed * Decimal(value) >= 0.5:
            raise ValueError('Wynik mnożenia prędkości podstawowej i mnożnika nie może być większy lub równy 0.5.')
        return Decimal(value)

    
    def _update_speed_multiplier(self):
        pass

    @property
    def speed(self) -> Decimal:
        """Metoda zwraca prędkość aktora. Prędkość jest wynikiem mnożenia prędkości podstawowej oraz mnożnika.

        :return: Prędkość aktora
        :rtype Decimal
        """
        return self.multiplier * self._base_speed

    @classmethod
    def get_instance(cls, state : GameState) -> 'Actor':
        """Zwraca instancję aktora.

        :return: Instancja aktora.
        :rtype: Actor
        """
        return getattr(state, f'a_{cls.__name__}')

    @abstractmethod
    def get_target() -> Tuple[int, int]:
        """Zwraca cel, do którego aktor ma się udać.

        :return: Pozycja celu w postaci krotki (x, y).
        :rtype: Tuple[int, int]
        """

    @abstractmethod
    def to_csv_line(self):
        pass

    @abstractmethod
    def get_csv_header(self):
        pass

    
    def select_future_direction(self, commit : Transaction):
        """Ustawia przyszyły kierunek ruchu aktora (`self.future_direction`). Wywoływana na skrzyżowaniach.
        Domyślnie nie robi nic, ale może być nadpisana w klasach dziedziczących. 
        """
        pass


    def on_hit_wall(self, current_pos : PrecisePosition, next_pos: PrecisePosition, wall_hit : Position) -> PrecisePosition:
        """Metoda wywoływana, gdy aktor próbuje przejść przez ścianę.
        Domyślnie, w tym wypadku wybrana jest pozycja najbardziej zbliżona do ściany, znajdująca się w linii między current_pos a next_pos.

        :param current_pos: Aktualna pozycja aktora.
        :type current_pos: PrecisePosition
        :param next_pos: Pozycja, do której aktor próbuje się udać.
        :type next_pos: PrecisePosition
        :param wall_hit: Pozycja ściany, w którą aktor uderzył.
        :type wall_hit: Position
        """
        from decimal import ROUND_HALF_UP
        cnext_pos = Maze.to_center_pos(next_pos)
        cwall = Maze.to_center_pos(wall_hit)

        is_colliding = [(cn - cw).copy_abs() < 1 for (cn, cw) in zip(cnext_pos, cwall)]
        was_changed = [a != b for (a, b) in zip(current_pos, next_pos)]

        ret : List[Decimal, Decimal] = [None, None]
        for i in range(2):
            if is_colliding[i] and was_changed[i]:
                ret[i] = current_pos[i].to_integral(ROUND_HALF_UP)
            else:
                ret[i] = next_pos[i]
            

        return tuple(ret)
    
    @staticmethod
    def _get_path_center_block(current_pos: PrecisePosition, next_pos: PrecisePosition) -> PrecisePosition:
        """Zwraca blok centralny ścieżki między dwoma pozycjami.

        :param current_pos: Aktualna pozycja aktora.
        :type current_pos: PrecisePosition
        :param next_pos: Następna pozycja aktora.
        :type next_pos: PrecisePosition
        :return: Pozycja bloku centralnego ścieżki.
        :rtype: Position
        """
        path_center = TupleOperations.divide_by_scalar(TupleOperations.add_tuples(current_pos, next_pos), Decimal(2))
        path_center_block = TupleOperations.round_tuple(path_center)
        return int(path_center_block[0]), int(path_center_block[1])


    def _check_if_intersection_crossed(self, current_pos : PrecisePosition, raw_next_pos : PrecisePosition) -> Decimal:
        """Sprawdza czy następny ruch aktora spowoduje przekroczenie skrzyżowania. Jeżeli tak zwraca ile przekroczył.


        :param current_pos: Aktualna pozycja aktora.
        :type current_pos: PrecisePosition
        :param next_pos: Następna pozycja aktora.
        :type next_pos: PrecisePosition
        :return: Liczba nieujemna jeżeli przekroczył, jeżeli nie przekroczył to -1. 
        :rtype: Decimal.
        """
        offset = TupleOperations.subtract_tuples(raw_next_pos, current_pos)
        # To działa jedynie wtedy jeżeli aktor porusza się w jednym kierunku. Dodatkowo to sprawdzam.
        if offset[0] != 0 and offset[1] != 0:
            raise ValueError("Aktor może poruszać się tylko w jednym kierunku.")


        # Sprawdź który blok może aktywować
        path_center_block = Actor._get_path_center_block(current_pos, raw_next_pos)
        if not self.is_intersection(self._maze.handle_outside_positions(path_center_block)): return Decimal(-1)

        # Spr

        # Oblicz dystansy
        distance_from_center = sum(TupleOperations.subtract_tuples(path_center_block, current_pos))
        distance_traversed = sum(TupleOperations.subtract_tuples(raw_next_pos, current_pos))
        
        if distance_from_center < 0:
            distance_from_center = -distance_from_center
            distance_traversed = -distance_traversed

        # Sprawdź czy przeszedł przez środek środek
        if distance_traversed >= distance_from_center:
            return distance_traversed - distance_from_center
        else:
            return Decimal(-2)

    def _handle_reverse_signal(self):
        if self.reverse_direction:
            self.direction = self.direction.add_rotation(Direction.DOWN)
            self.reverse_direction = False

    
    def is_intersection(self, pos):
        return self._maze.is_intersection(pos)

    def get_next_step(self, commit : Transaction, position : Position = None, precise_position : PrecisePosition = None, jump : Decimal = None, depth = 0) -> Tuple[Decimal, Decimal]:
        """Zwraca następny krok aktora w postaci krotki (x, y).
        Respektuje metodę pause

        :param position: Pozycja, z której aktor ma się poruszyć. Jeżeli nie podano, to używana jest aktualna pozycja.
        :type position: Position
        :param precise_position: Dokładna pozycja, z której aktor ma się poruszyć. Jeżeli nie podano, to używana jest aktualna dokładna pozycja.
        :type precise_position: PrecisePosition
        :param jump: Długość skoku aktora. Jeżeli nie podano, to używana jest aktualna długość skoku. Długość skoku musi być < 1.
        :type jump: Decimal
        :param depth: Głębokość rekurencji.
        :type depth: int
        :return: Następny krok w postaci krotki (x, y).
        :rtype: Tuple[float, float]
        """
        gt = commit.get_temp
        wt = commit.write_temp

        if position is None:
            position = self.get_position()
        if precise_position is None:
            precise_position = self.get_precise_position()
        if jump is None:
            jump = self.speed
        changed_blocks = gt('_prev_block') != position

        def on_intersection():
            wt('direction', gt('future_direction'))

        if jump >= 1: 
            raise ValueError("Długość skoku musi być mniejsza niż 1. Obecna długość skoku: {}".format(jump))

        if changed_blocks:
            self._handle_reverse_signal()

        raw_future = self._maze.shift_position(precise_position, gt('direction'), jump, handle_outside=False)
        future_pos = self._maze.handle_outside_positions(raw_future)
        next_block = self._maze.shift_position(position, gt('direction'))

        if gt('_pause') > 0 and depth == 0:
            wt('_pause', gt('_pause') - 1)
            return precise_position
        # Jeżeli aktor uderzył w ścianę, to zatrzymujemy go
        ## Najpierw sprawdzamy czy dotyka następnego pola

        cfuture_pos = Maze.to_center_pos(future_pos)
        cnext_block = Maze.to_center_pos(next_block)

        is_touching = (cfuture_pos[0] - cnext_block[0]).copy_abs() < 1 or (cfuture_pos[1] - cnext_block[1]).copy_abs() < 1



        # Jeżeli już było wykonywane dalszej części nie należy sprawdzać



        # Zaktualizuj poprzedni blok

        if changed_blocks:
            wt('_prev_block', self.get_position())


        # Ponieważ duch musi myśleć o 1 krok do przodu, to jeżeli następnym krokiem będzie skrzyżowanie, to wybieramy kierunek.
        # Aby to zrobić w ostatniej chwili sprawdzam, czy następna pozycja znajduje się w innym bloku
        future_block = TupleOperations.round_tuple(future_pos)
        is_about_to_change_block = future_block != position
        if is_about_to_change_block and depth == 0 and self.is_intersection(future_block):
            self.select_future_direction(commit)

        # Obsłuż zmiany kierunków

        intersection_crossed = self._check_if_intersection_crossed(precise_position, raw_future)
        if intersection_crossed >= 0 and depth == 0:
            raw_intersection_pos = self._maze.handle_outside_positions(Actor._get_path_center_block(precise_position, raw_future))
            on_intersection()
        

        if intersection_crossed > 0 and depth == 0:
            return self.get_next_step(commit, raw_intersection_pos, tuple([Decimal(raw_intersection_pos[0]), Decimal(raw_intersection_pos[1])]), intersection_crossed, depth + 1)
        
        if self._maze.check_wall(next_block) and is_touching:
            future_pos = self.on_hit_wall(precise_position, future_pos, next_block)

        # Dodatkowo jeżeli stoi na skrzyżowaniu wykonuj on_intersection
        if self.is_intersection(position) and depth == 0 and future_pos == position:
            on_intersection()


        return future_pos
    
    @property
    def intersection_next_move(self):
        # Nie powinno być problemu z pauzą spowodowaną zjedzeniem owoca
        # Pauza zaczyna się po wejściu na blok, najdalsza możliwa pozycja jest poniżej 1
        position = self.get_position()
        precise_position = self.get_precise_position()
        future_position = self._maze.shift_position(precise_position, self.direction, self.speed)
        future_block = TupleOperations.round_tuple(future_position)

        changed_blocks = future_block != position
        return changed_blocks and self.is_intersection(future_block)
    
    @property
    def about_to_change_blocks(self):
        position = self.get_position()
        precise_position = self.get_precise_position()
        future_position = self._maze.shift_position(precise_position, self.direction, self.speed)
        future_block = TupleOperations.round_tuple(future_position)

        changed_blocks = future_block != position
        return changed_blocks

    def kill(self):
        """Metoda wywoływana przy śmierci aktora.
        Domyślnie ustawia kierunek na prawo i uruchamia respawn.
        """
        pass

    def on_spawn(self):
        """Metoda wywoływana przy respawnie aktora.
        Domyślnie ustawia kierunek na prawo.
        """
        game : GameCore = GameCore.get_main_instance()
        game.register_frame_hook(self.on_game_update, priority_group=1)
        game.register_frame_hook(self.commit_changes, priority_group=2)
        game.register_frame_hook(self._detect_collisions, priority_group=3)

    def on_game_update(self, current_state: GameState):
        """Metoda wywoływana przy aktualizacji stanu gry. 
        W celu uniknięcia częściowych aktualizacji, zmienne widoczne z zewnątrz powinny być dopiero aktualizowane w `post_game_update`.

        :param current_state: Aktualny stan gry.
        :type current_state: GameState
        """
        self._transaction = Transaction(self)
        # New_pos nie jest zarządzany przez system transakcji ponieważ konieczne jest wykorzystanie metody set_position
        self.new_pos = self.get_next_step(commit=self._transaction)

    def commit_changes(self, current_state: GameState):
        """Metoda wywoływana po aktualizacji wszystkich aktorów. Służy do zatwierdzenia zmian w stanie aktora.

        :param current_state: Aktualny stan gry.
        :type current_state: GameState
        """
        self._transaction.commit()
        self.set_position(self.new_pos)

    def _detect_collisions(self, current_state: GameState):
        """Metoda wykrywa i zapisuje wykryte kolizje z innymi obiektami
        """
        from src.general.maze import Collidable
        global detected_collisions
        maze = self._maze

        pos = self.get_position()
        objects = maze.get_objects_at(pos)

        for object in objects:
            # Sprawdź czy z objektem można zajść w kolizję i upewnij się że ten obiekt jest inny niż obecny
            if isinstance(object, Collidable) and id(object) != id(self):
                detected_collisions.add((self, object))
        

    def _get_filled_ratio(self):
        gc : GameCore = GameCore.get_main_instance()
        return gc.get_game_config().ACTOR_FILLED_RATIO
    
    def _get_named_layer(self):
        return 'actors'
    
    def destroy(self):
        raise NotImplementedError("Nie zaimplementowano")
        
    def pause(self, frames : int):
        """Wstrzymuje ruch pacmana na określoną ilość klatek.

        :param frames: 
        :type frames: int
        """
        self._pause = frames



    

from src.general import reload_functions
def _reload():
    global detected_collisions, detected_last_time
    detected_collisions = set()
    detected_last_time = set()
    Actor._reload_all()
reload_functions.append(_reload)