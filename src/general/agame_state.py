from abc import ABC, abstractmethod
from typing import Self

class AGameState(ABC):
    
    from typing import List
    from pygame import event
    

    def __init__(self):
        self.score = 0
        self.is_game_over = False
        self.events = []

    @abstractmethod
    def copy(self) -> Self:
        pass

    @abstractmethod
    def to_list(self) -> List[str]:
        """Metoda abstrakcyjna zwracająca stan gry jako listę. Funkcja wykorzystywana do zapisu stanu gry do pliku.

        Returns:
            list[str]: Stan gry jako lista. Część elementów, takich jak event może zostać pominięta.
        """
        pass

    @abstractmethod
    def get_headers(self) -> List[str]:
        """Metoda zwracająca nagłówki kolumn do pliku CSV. Funkcja wykorzystywana do zapisu stanu gry do pliku.

        Returns:
            List[str]: Nagłówki kolumn do pliku CSV. Część elementów, takich jak event może zostać pominięta.
        """
        pass
