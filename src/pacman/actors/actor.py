from typing import *
from src.pacman.maze import MazeObject, Maze
from abc import ABC, abstractmethod
from src.general import Direction
from src.pacman.game_core import GameCore, GameState
from collections import deque
from decimal import Decimal, ROUND_UP, ROUND_HALF_UP

detected_collisions = deque()

def execute_on_collisions(_):
    from src.pacman.maze.collidable import Collidable
    while len(detected_collisions) != 0:
        collision : Tuple['Actor', Collidable] = detected_collisions.popleft()
        actor, collidable = collision
        collidable.on_collision(actor)

    

class Actor(MazeObject):
    """Klasa reprezentująca aktora w grze Pacman, dziedzicząca po MazeObject.
    Aktorzy mogą poruszać się po labiryncie i posiadają stan.
    """
    registered_collision_hooks = False

    def __init__(self, maze : Maze, respawn_interval: int = 0, name: str = "Actor", spawn: Tuple[int, int] = None, base_speed=None):
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

        self.maze = maze
        self.new_pos = 0
        self.multiplier = Decimal('1.0')
        self.prev_pos = (0,0)
        super().__init__(spawn)
        self.respawn_interval = respawn_interval
        self.name = name
        self.direction = Direction.RIGHT
        self.base_speed = base_speed
    
    def get_spawn_point(self) -> Tuple[int, int]:
        """Zwraca punkt startowy aktora w postaci krotki (x, y).
        :param maze: Obiekt labiryntu, w którym aktor będzie się poruszał.
        :type maze: Maze
        :return: Punkt startowy aktora.
        :rtype: Tuple[int, int]
        """
        from src.pacman.maze.spawn_manager import SpawnManager
        return SpawnManager._get_spawn_point(self)
    
    def set_speed_multiplier(self, multiplier : Decimal):
        """Ustawia mnożnik prędkości aktora. Ostateczna prędkość jest wynikiem mnożenia prędkości podstawowej oraz mnożnika.

        :param speed: Prędkość aktora.
        :type speed: Decimal
        :raises ValueError: Zgłasza w przypadku podania mnożnika na tyle dużego, że prędkość ostateczna jest większa niż 1. Jest to zabezpieczenie przed pomijaniem bloków.
        """        
        if self.base_speed * Decimal(self.multiplier) > 1:
            raise ValueError('Wynik mnożenia prędkości podstawowej i mnożnika większy niż 1.')
        self.multiplier = Decimal(self.multiplier)

    

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

    def on_hit_wall(self, current_pos : Tuple[Decimal,Decimal], next_pos: Tuple[Decimal, Decimal]) -> Tuple[Decimal, Decimal]:
        """Metoda wywoływana, gdy aktor próbuje przejść przez ścianę.
        Domyślnie w tym wypadku aktor jest zatrzymywany i nie zmienia swojej pozycji.

        :param current_pos: Aktualna pozycja aktora.
        :type current_pos: Tuple[Decimal, Decimal]
        :param next_pos: Pozycja, do której aktor próbuje się udać.
        :type next_pos: Tuple[Decimal, Decimal]
        """

        return current_pos

    def get_next_step(self) -> Tuple[Decimal, Decimal]:
        """Zwraca następny krok aktora w postaci krotki (x, y).

        :return: Następny krok w postaci krotki (x, y).
        :rtype: Tuple[float, float]
        """
        pos = self.get_position()
        prec_pos = self.get_precise_position()
        is_intersection = self.maze.is_intersection(pos)
        is_in_center = prec_pos[0] % Decimal(1) == 0 and prec_pos[1] % Decimal(1) == 0

        
        if is_intersection and is_in_center:
           self.on_intersection()
        future_pos = Maze.shift_position(prec_pos, self.direction, self.get_speed())
        next_block = Maze.shift_position(pos, self.direction)
        if self.maze.check_wall(next_block) and is_in_center:
            future_pos = self.on_hit_wall(prec_pos, future_pos)
        future_pos[1].to_integral_value
        # Ponieważ duch musi myśleć o 1 krok do przodu, to jeżeli następnym krokiem będzie skrzyżowanie, to wybieramy kierunek.
        # Aby to zrobić w ostatniej chwili sprawdzam, czy następna pozycja znajduje się w innym bloku
        future_block = (future_pos[0].to_integral_value(ROUND_HALF_UP), future_pos[1].to_integral_value(ROUND_HALF_UP))
        is_about_to_change_block = future_block != pos

        if is_about_to_change_block and self.maze.is_intersection(future_block):
            self.select_future_direction()

        return future_pos


    def on_death(self):
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
        from src.pacman.maze.collidable import Collidable
        global detected_collisions
        maze = self.maze

        pos = self.get_position()
        objects = maze.get_objects_at(pos)

        for object in objects:
            # Sprawdź czy z objektem można zajść w kolizję i upewnij się że ten obiekt jest inny niż obecny
            if isinstance(object, Collidable) and id(object) != id(self):
                detected_collisions.append((self, object))
        

    def _get_filled_ratio(self):
        gc : GameCore = GameCore.get_main_instance()
        return gc.get_game_config().ACTOR_FILLED_RATIO
    
    def _get_named_layer(self):
        return 'actors'
    
    def destroy(self):
        raise NotImplementedError("Nie zaimplementowano")

    


