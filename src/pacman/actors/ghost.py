from .actor import Actor
from .ghost_state import GhostState
from abc import ABC, abstractmethod
from src.general import Direction
from typing import *
from src.pacman.maze import Maze
import array

class Ghost(Actor):
    """Klasa implementująca aktora typu Ghost w grze pacman
    """

    ghosts : List['Ghost'] = []
    
    

    def __init__(self, respawn_interval: int = 0, name: str = "Ghost"):
        """Inicjalizuje aktora typu Ghost na podstawie punktu startowego i interwału respawnu.

        :param respawn_interval: Czas w sekundach po którym aktor zostanie zrespawnowany.
        :type respawn_interval: int
        :param name: Nazwa aktora.
        :type name: str
        """
        super().__init__(Maze.get_main_instance(), respawn_interval, name, (1,0)) # Ustawiam tak, aby obiekt później został przeniesiony do odpowiedniego miejsca. Tak, czy tak jest to w ścianie.
        self.set_state(GhostState.CHASE)  # Domyślny stan to SCATTER
        Ghost.ghosts.append(self)
        self.direction : Direction = Direction.RIGHT
        self._maze = Maze.get_main_instance()
        self.future_direction: Direction = Direction.RIGHT  # Kierunek, w którym duch ma się poruszać w przyszłości

    @abstractmethod
    def on_powerup_activated(self):
        """Metoda wywoływana, gdy power-up jest aktywowany.
        Powinna być zaimplementowana w klasach dziedziczących.
        """
        raise NotImplementedError("Metoda on_powerup_activated nie jest zaimplementowana.")
    
    @abstractmethod
    def on_powerup_deactivated(self):
        """Metoda wywoływana, gdy power-up jest dezaktywowany.
        Powinna być zaimplementowana w klasach dziedziczących.
        """
        raise NotImplementedError("Metoda on_powerup_deactivated nie jest zaimplementowana.")

    @classmethod
    def notify_instances_powerup_activated():
        """Powiadamia wszystkie instancje Ghost o aktywacji power-upa.
        """
        for ghost in Ghost.ghosts:
            ghost.on_powerup_activated()

    @classmethod
    def notify_instances_powerup_deactivated():
        """Powiadamia wszystkie instancje Ghost o dezaktywacji power-upa.
        """
        for ghost in Ghost.ghosts:
            ghost.on_powerup_deactivated()

    @abstractmethod
    def get_scatter_position(self) -> Tuple[int, int]:
        """Zwraca pozycję scatter dla tego ducha.

        :return: Pozycja scatter w postaci krotki (x, y).
        :rtype: Tuple[int, int]
        """
        raise NotImplementedError("Metoda get_scatter_position nie jest zaimplementowana.")
    
    @abstractmethod
    def get_chase_position(self) -> Tuple[int, int]:
        """Zwraca pozycję chase dla tego ducha.

        :return: Pozycja chase w postaci krotki (x, y).
        :rtype: Tuple[int, int]
        """
        raise NotImplementedError("Metoda get_chase_position nie jest zaimplementowana.")
    
    def get_state(self) -> GhostState:
        """Zwraca aktualny stan ducha.

        :return: Stan ducha.
        :rtype: GhostState
        """
        return self.state
    
    def set_state(self, state: GhostState):
        """Ustawia stan ducha.

        :param state: Stan ducha do ustawienia.
        :type state: GhostState
        """
        self.state = state


    def get_target(self) -> Tuple[int, int]:
        """Zwraca cel, do którego duch ma się udać.
        Metoda może zwrócić pozycję do której duch nie może się udać.


        :return: Pozycja celu w postaci krotki (x, y).
        :rtype: Tuple[int, int]
        """
        state = self.get_state()

        if state == GhostState.SCATTER:
            return self.get_scatter_position()
        elif state == GhostState.CHASE:
            return self.get_chase_position()

    def on_intersection(self):
        self.direction = self.future_direction
        
    def select_future_direction(self):
        """Wybiera następny kierunek ruchu ducha
        """
        target_pos = self.get_target()

        # Przesuń pozycję ducha o 1 krok
        next_pos = Maze.move_one_step(self.position, self.direction)

        
        # Teraz sprawdź, wszystkie kierunki wokół next_pos

        check_positions = [
            (next_pos[0], next_pos[1] - 1),  # UP
            (next_pos[0] - 1, next_pos[1]),  # LEFT
            (next_pos[0], next_pos[1] + 1),   # DOWN
            (next_pos[0] + 1, next_pos[1])  # RIGHT
        ]

        # Z wyjątkiem obecnej

        check_positions[check_positions.index(self.position)] = (999999999, 999999999)  # Ustaw na coś co nie jest możliwe

        # Uniemożliwiaj ściany
        for i in range(len(check_positions)):
            if self.maze.check_wall(check_positions[i]):
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


        self.future_direction = winner[0]

            






    
        
        
        


            