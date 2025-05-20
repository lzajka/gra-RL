from enum import Enum
from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT

class Direction(Enum):
    UP = K_UP
    DOWN = K_DOWN
    LEFT = K_LEFT
    RIGHT = K_RIGHT

    def opposite(self):
        '''Metoda zwraca przeciwny kierunek'''
        return self.add_rotation(Direction.DOWN)
        
    def add_rotation(self, rotation : 'Direction', in_place=False) -> 'Direction':
        """

        :param rotation: Obrót do dodania
        :type rotation: Direction
        :param in_place: Czy dodać obrót w miejscu
        :type in_place: bool, domyślnie False
        """

        a = self.to_ordered_int()
        b = rotation.to_ordered_int()

        c = (a + b) % 4

        new = from_ordered_int(c)
        if in_place:
            self = new
        return new

    def remove_rotation(self, rotation : 'Direction', in_place=False) -> 'Direction':
        """Metoda usuwa obrót z kierunku.

        :param rotation: Obrót do usuniecia
        :type rotation: Direction
        :return: _description_
        :rtype: _type_
        """
        a = self.to_ordered_int()
        b = rotation.to_ordered_int()
        
        c = (4 + a - b) % 4

        new = from_ordered_int(c)
        if in_place:
            self = new
        return new
    
    def to_ordered_int(self) -> int:
        """Metoda zwraca kierunek jako liczbę całkowitą w kolejności UP, RIGHT, DOWN, LEFT
        :return: Kierunek jako liczba całkowita
        :rtype: int
        """
        return {
            Direction.UP: 0,
            Direction.RIGHT: 1,
            Direction.DOWN: 2,
            Direction.LEFT: 3
        }[self]
    
    
    
def from_ordered_int(value: int) -> Direction:
        """Metoda przekształca liczbę całkowitą na kierunek.
        Metoda zwraca kierunek jako liczbę całkowitą w kolejności UP, RIGHT, DOWN, LEFT

        :param value: Liczba całkowita reprezentująca kierunek
        :type value: int
        :return: Kierunek
        :rtype: Direction
        """

        return {
            0: Direction.UP,
            1: Direction.RIGHT,
            2: Direction.DOWN,
            3: Direction.LEFT
        }[value]

        
