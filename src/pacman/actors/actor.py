from typing import *
from src.general.maze import MazeObject, Collidable, Maze
from abc import ABC, abstractmethod
from src.general import Direction
from src.pacman.game_core import GameCore, GameState
from collections import deque
from decimal import Decimal, ROUND_DOWN
from .status_effects import SpeedStatusEffect
from src.general.utils import TupleOperations
from src.general.maze import PrecisePosition, Position
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

    def __init__(self, parent : Maze, respawn_interval: int = 0, name: str = "Actor", spawn: Tuple[int, int] = None, base_speed=None):
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
        if not Actor.registered_collision_hooks:
            game : GameCore = GameCore.get_main_instance()
            game.register_frame_hook(execute_on_collisions, priority_group=4)
            Actor.registered_collision_hooks = True

        if base_speed is None:
            base_speed = GameCore.get_main_instance().get_game_config().BASE_SPEED

        self.new_pos = 0
        self.multiplier = Decimal('1.0')
        super().__init__(spawn, parent)
        self.respawn_interval = respawn_interval
        self.name = name
        self.direction = Direction.RIGHT
        self.base_speed = base_speed
        self._pause = 0
        self.prev_block = (Decimal(-1), Decimal(-1))
        self.status_effects = dict()
        self.apply_speed_status_effect(SpeedStatusEffect.NORM)
        self.reverse_direction = False


    @abstractmethod
    def get_status_effect_speed_modifier(self, state : SpeedStatusEffect, level) -> Decimal:
        pass
    
    def apply_speed_status_effect(self, state: SpeedStatusEffect):
        """Ustawia stan aktora.

        :param state: Stan aktora do ustawienia.
        :type state: ActorState
        """
        gs : GameState = GameState.get_main_instance()
        level = gs.level
        speed_modifier = self.get_status_effect_speed_modifier(state, level)

        if speed_modifier is None:
            # Zwracając None informuje, że dany stan nie występuje
            return
        
        self.status_effects[state] = speed_modifier
        self.set_speed_multiplier(speed_modifier)
    
    def clear_status_effect(self, state : SpeedStatusEffect):
        """Czyści stan aktora."""
        if state == SpeedStatusEffect.NORM:
            raise ValueError("Nie można usunąć stanu NORM. Jest on stanem podstawowym, na który nakładane są poszczególne stany.")
        
        if state not in self.status_effects:
            return
        
        del self.status_effects[state]

        slowest = Decimal('1.0')  # Ustawiam na maksymalną prędkość
        # Wybierz najmniejszą prędkość
        for speed in self.status_effects.values():
            if speed < slowest:
                slowest = speed

        self.set_speed_multiplier(slowest)

    def toggle_status_effect(self, state : SpeedStatusEffect):
        """Przełącza stan prędkości aktora.

        :param state: Stan prędkości do przełączenia.
        :type state: SpeedStatusEffect
        """
        if state in self.status_effects:
            self.clear_status_effect(state)
        else:
            self.apply_speed_status_effect(state)

    
    def set_speed_multiplier(self, multiplier : Decimal):
        """Ustawia mnożnik prędkości aktora. Ostateczna prędkość jest wynikiem mnożenia prędkości podstawowej oraz mnożnika.

        :param speed: Prędkość aktora.
        :type speed: Decimal
        :raises ValueError: Zgłasza w przypadku podania mnożnika na tyle dużego, że prędkość ostateczna jest większa niż 1. Jest to zabezpieczenie przed pomijaniem bloków.
        """        
        if self.base_speed * Decimal(self.multiplier) > 1:
            raise ValueError('Wynik mnożenia prędkości podstawowej i mnożnika większy niż 1.')
        self.multiplier = Decimal(multiplier)

    def get_speed_multiplier(self) -> Decimal:
        """Zwraca mnożnik prędkości aktora.

        :return: Mnożnik prędkości aktora
        :rtype: Decimal
        """
        return self.multiplier

    def get_speed(self) -> Decimal:
        """Metoda zwraca prędkość aktora. Prędkość jest wynikiem mnożenia prędkości podstawowej oraz mnożnika.

        :return: Prędkość aktora
        :rtype Decimal
        """
        return self.multiplier * self.base_speed

    @classmethod
    @abstractmethod
    def get_instance() -> 'Actor':
        """Zwraca instancję aktora.

        :return: Instancja aktora.
        :rtype: Actor
        """
        pass

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

    
    def select_future_direction(self):
        """Ustawia przyszyły kierunek ruchu aktora (`self.future_direction`). Wywoływana na skrzyżowaniach.
        Domyślnie nie robi nic, ale może być nadpisana w klasach dziedziczących. 
        """
        pass

    def on_intersection(self):
        """Metoda wywoływana, gdy aktor znajduje się na skrzyżowaniu.
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
        from decimal import ROUND_DOWN
        cnext_pos = Maze.to_center_pos(next_pos)
        cwall = Maze.to_center_pos(wall_hit)

        is_colliding = [(cn - cw).copy_abs() < 1 for (cn, cw) in zip(cnext_pos, cwall)]
        was_changed = [a != b for (a, b) in zip(current_pos, next_pos)]

        ret = [None, None]
        for i in range(2):
            if is_colliding[i] and was_changed[i]:
                ret[i] = cnext_pos[i].to_integral_value(ROUND_DOWN)
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


    def _check_if_intersection_crossed(self, current_pos : PrecisePosition, next_pos : PrecisePosition) -> Decimal:
        """Sprawdza czy następny ruch aktora spowoduje przekroczenie skrzyżowania. Jeżeli tak zwraca ile przekroczył.


        :param current_pos: Aktualna pozycja aktora.
        :type current_pos: PrecisePosition
        :param next_pos: Następna pozycja aktora.
        :type next_pos: PrecisePosition
        :return: Liczba nieujemna jeżeli przekroczył, jeżeli nie przekroczył to -1. 
        :rtype: Decimal.
        """
        offset = TupleOperations.subtract_tuples(next_pos, current_pos)
        # To działa jedynie wtedy jeżeli aktor porusza się w jednym kierunku. Dodatkowo to sprawdzam.
        if offset[0] != 0 and offset[1] != 0:
            raise ValueError("Aktor może poruszać się tylko w jednym kierunku.")


        # Sprawdź który blok może aktywować
        path_center_block = Actor._get_path_center_block(current_pos, next_pos)
        if not self.maze.is_intersection(path_center_block): return Decimal(-1)

        # Spr

        # Oblicz dystansy
        distance_from_center = sum(TupleOperations.subtract_tuples(path_center_block, current_pos))
        distance_traversed = sum(TupleOperations.subtract_tuples(next_pos, current_pos))
        
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

    def get_next_step(self, position : Position = None, precise_position : PrecisePosition = None, jump : Decimal = None, depth = 0) -> Tuple[Decimal, Decimal]:
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
        if position is None:
            position = self.get_position()
        if precise_position is None:
            precise_position = self.get_precise_position()
        if jump is None:
            jump = self.get_speed()

        changed_blocks = self.prev_block != position

        if jump >= 1: 
            raise ValueError("Długość skoku musi być mniejsza niż 1. Obecna długość skoku: {}".format(jump))

        if changed_blocks:
            self._handle_reverse_signal()

        future_pos = self.maze.shift_position(precise_position, self.direction, jump)
        next_block = self.maze.shift_position(position, self.direction)

        if self._pause > 0 and depth == 0:
            self._pause -= 1
            return precise_position
        # Jeżeli aktor uderzył w ścianę, to zatrzymujemy go
        ## Najpierw sprawdzamy czy dotyka następnego pola

        cfuture_pos = Maze.to_center_pos(future_pos)
        cnext_block = Maze.to_center_pos(next_block)

        is_touching = (cfuture_pos[0] - cnext_block[0]).copy_abs() < 1 or (cfuture_pos[1] - cnext_block[1]).copy_abs() < 1



        # Jeżeli już było wykonywane dalszej części nie należy sprawdzać

        # Obsłuż zmiany kierunków

        intersection_crossed = self._check_if_intersection_crossed(precise_position, future_pos)

        if intersection_crossed >= 0 and depth == 0:
            intersection_pos = Actor._get_path_center_block(precise_position, future_pos)
            self.on_intersection()

        # Zaktualizuj poprzedni blok

        if changed_blocks:
            self.prev_block = self.get_position()

        if intersection_crossed > 0 and depth == 0:
            return self.get_next_step(intersection_pos, tuple([Decimal(intersection_pos[0]), Decimal(intersection_pos[1])]), intersection_crossed, depth + 1)

        
        if self.maze.check_wall(next_block) and is_touching:
            future_pos = self.on_hit_wall(precise_position, future_pos, next_block)

        # Dodatkowo jeżeli stoi na skrzyżowaniu wykonuj on_intersection
        if self.maze.is_intersection(position) and depth == 0 and future_pos == position:
            self.on_intersection()

        # Ponieważ duch musi myśleć o 1 krok do przodu, to jeżeli następnym krokiem będzie skrzyżowanie, to wybieramy kierunek.
        # Aby to zrobić w ostatniej chwili sprawdzam, czy następna pozycja znajduje się w innym bloku
        future_block = TupleOperations.round_tuple(future_pos)

        is_about_to_change_block = future_block != position

        if is_about_to_change_block and depth == 0 and self.maze.is_intersection(future_block):
            self.select_future_direction()

        return future_pos
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
        self.new_pos = self.get_next_step()

    def commit_changes(self, current_state: GameState):
        """Metoda wywoływana po aktualizacji wszystkich aktorów. Służy do zatwierdzenia zmian w stanie aktora.

        :param current_state: Aktualny stan gry.
        :type current_state: GameState
        """
        self.set_position(self.new_pos)

    def _detect_collisions(self, current_state: GameState):
        """Metoda wykrywa i zapisuje wykryte kolizje z innymi obiektami
        """
        from src.general.maze import Collidable
        global detected_collisions
        maze = self.maze

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



    


