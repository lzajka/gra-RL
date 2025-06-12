from .actor import Actor
from .ghost_state import GhostState
from abc import ABC, abstractmethod
from src.general import Direction
from typing import *
from src.pacman.maze import Maze

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
        self.set_state(GhostState.SCATTER)  # Domyślny stan to SCATTER
        Ghost.ghosts.append(self)
        self._direction : Direction = Direction.RIGHT
        self._maze = Maze.get_main_instance()

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
    
    def choose_direction():
        """Zwraca kierunek, w którym duch ma się poruszać.
        W przypadku ducha kierunek wybierany jest o 1 krok w 
        """

        
    def pick_next_direction(self, target: Tuple[int, int]) -> Direction:
        """Wybiera następny kierunek ruchu ducha na podstawie celu.

        :param target: Cel, do którego duch ma się udać.
        :type target: Tuple[int, int]
        :return: Wybrany kierunek ruchu.
        :rtype: Direction
        """
        # Implementacja logiki wyboru kierunku na podstawie celu
        # Może być oparta na algorytmie A* lub BFS
        raise NotImplementedError("Metoda pick_next_direction nie jest zaimplementowana.")
    
        
        
        


            