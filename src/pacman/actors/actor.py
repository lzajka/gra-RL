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
        from src.pacman.maze.spawn_manager import SpawnManager
        self.maze = maze
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
    def on_spawn(self):
        self.direction = Direction.RIGHT


    @abstractmethod
    def get_target() -> Tuple[int, int]:
        """Zwraca cel, do którego aktor ma się udać.

        :return: Pozycja celu w postaci krotki (x, y).
        :rtype: Tuple[int, int]
        """

    @abstractmethod
    def to_csv_line():
        pass

    @abstractmethod
    def get_csv_header():
        pass

    @abstractmethod
    def choose_direction() -> Direction:
        """Zwraca kierunek, w którym aktor ma się poruszać.

        :return: Kierunek ruchu aktora.
        :rtype: Direction
        """
        pass

    def get_next_step(self) -> Tuple[int, int]:
        """Zwraca następny krok aktora w postaci krotki (x, y).

        :return: Następny krok w postaci krotki (x, y).
        :rtype: Tuple[int, int]
        """
        pos = self.get_position()

        if self.maze.is_intersection(pos):
           self.direction = self.choose_direction()
        
        pos2 = None

        if self.direction == Direction.LEFT:
            pos2 = (self.position[0] - 1, self.position[1])
        elif self.direction == Direction.RIGHT:
            pos2 =(self.position[0] + 1, self.position[1])
        elif self.direction == Direction.UP:
            pos2 = (self.position[0], self.position[1] - 1)
        elif self.direction == Direction.DOWN:
            pos2 = (self.position[0], self.position[1] + 1)
        
        if self.maze.check_wall(pos2):
            return pos
        else:
            return pos2

    def on_death(self):
        """Metoda wywoływana przy śmierci aktora.
        Domyślnie ustawia kierunek na prawo i uruchamia respawn.
        """
        pass

    def on_spawn(self):
        """Metoda wywoływana przy respawnie aktora.
        Domyślnie ustawia kierunek na prawo.
        """
        self.direction = Direction.RIGHT
        GameCore.get_main_instance().register_frame_hook(self.on_game_update)


    def on_game_update(self, current_state: GameState):
        """Metoda wywoływana przy aktualizacji stanu gry.

        :param current_state: Aktualny stan gry.
        :type current_state: GameState
        """
        
        new_pos = self.get_next_step()
        self.set_position(new_pos)

    


