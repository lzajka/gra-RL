from typing import *
from src.pacman.maze import MazeObject, Maze
from abc import ABC, abstractmethod
from src.general import Direction
from src.pacman.game_core import GameCore, GameState

class Actor(MazeObject):
    """Klasa reprezentująca aktora w grze Pacman, dziedzicząca po MazeObject.
    Aktorzy mogą poruszać się po labiryncie i posiadają stan.
    """

    def __init__(self, maze : Maze, respawn_interval: int = 0, name: str = "Actor", spawn: Tuple[int, int] = None):
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
        self.maze = maze
        self.new_pos = 0
        super().__init__(spawn)
        self.respawn_interval = respawn_interval
        self.name = name
        self.direction = Direction.RIGHT
    
    def get_spawn_point(self) -> Tuple[int, int]:
        """Zwraca punkt startowy aktora w postaci krotki (x, y).
        :param maze: Obiekt labiryntu, w którym aktor będzie się poruszał.
        :type maze: Maze
        :return: Punkt startowy aktora.
        :rtype: Tuple[int, int]
        """
        from src.pacman.maze.spawn_manager import SpawnManager
        return SpawnManager._get_spawn_point(self)

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

    def on_hit_wall(self, current_pos : Tuple[int,int], next_pos: Tuple[int, int]) -> Tuple[int, int]:
        """Metoda wywoływana, gdy aktor próbuje przejść przez ścianę.
        Domyślnie w tym wypadku aktor jest zatrzymywany i nie zmienia swojej pozycji.

        :param current_pos: Aktualna pozycja aktora.
        :type current_pos: Tuple[int, int]
        :param next_pos: Pozycja, do której aktor próbuje się udać.
        :type next_pos: Tuple[int, int]
        """

        return current_pos

    def get_next_step(self) -> Tuple[int, int]:
        """Zwraca następny krok aktora w postaci krotki (x, y).

        :return: Następny krok w postaci krotki (x, y).
        :rtype: Tuple[int, int]
        """
        pos = self.get_position()

        if self.maze.is_intersection(pos):
           self.on_intersection()
        
        future_pos = Maze.shift_position(pos, self.direction)

        if self.maze.check_wall(future_pos):
            future_pos = self.on_hit_wall(pos, future_pos)

        # Ponieważ duch musi myśleć o 1 krok do przodu, to jeżeli następnym krokiem będzie skrzyżowanie, to wybieramy kierunek.
        if not self.maze.check_wall(future_pos) and self.maze.is_intersection(future_pos):
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
        game.register_frame_hook(self.post_game_update, priority_group=2)

    def on_game_update(self, current_state: GameState):
        """Metoda wywoływana przy aktualizacji stanu gry. 
        W celu uniknięcia częściowych aktualizacji, zmienne widoczne z zewnątrz powinny być dopiero aktualizowane w `post_game_update`.

        :param current_state: Aktualny stan gry.
        :type current_state: GameState
        """
        self.new_pos = self.get_next_step()

    def post_game_update(self, current_state: GameState):
        """Metoda wywoływana po aktualizacji wszystkich aktorów. Służy do zatwierdzenia zmian w stanie aktora.

        :param current_state: Aktualny stan gry.
        :type current_state: GameState
        """
        self.set_position(self.new_pos)

    def _get_filled_ratio(self):
        gc : GameCore = GameCore.get_main_instance()
        return gc.get_game_config().ACTOR_FILLED_RATIO
    
    def _get_named_layer(self):
        return 'actors'

    


