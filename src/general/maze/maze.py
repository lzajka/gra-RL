from typing import Tuple, List, Dict, Set
from src.general import Direction
from decimal import Decimal

class Maze:
    """Klasa przechowująca informacje na temat labiryntu oraz elementów, z których się składa.
    Labirynt to plansza 2D na której
    """
    def __init__(self):
        """Inicjalizuje labirynt na podstawie pliku.

        :param file_path: Ścieżka do pliku z danymi labiryntu.
        :type file_path: str
        """
        self.size = (0, 0)  # Rozmiar labiryntu w postaci krotki (szerokość, wysokość)
        
        self.objects_at : Dict[Tuple[int, int], Set] = {}  # Słownik przechowujący obiekty w labiryncie
    
    def copy(self) -> 'Maze':
        """Tworzy i zwraca kopię labiryntu.
        """
        new_maze = Maze()
        new_maze.size = self.size
        new_maze.objects_at = dict()
        #for pos, objects in self.objects_at.items():
        #    objects2 = set()
        #    for obj in objects:
        #        new_obj = obj.copy()
        #        objects2.add(new_obj)
        #    new_maze.objects_at[pos] = objects2
        #return new_maze
            
    @staticmethod
    def shift_position(origin : Tuple[Decimal, Decimal], direction : Direction, steps: Decimal = 1) -> Tuple[Decimal, Decimal]:
        """Przesuwa pozycję o jeden krok w danym kierunku.

        :param origin: Pozycja początkowa w postaci krotki (x, y).
        :type origin: Tuple[Decimal, Decimal]
        :param direction: Kierunek, w którym ma nastąpić przesunięcie.
        :type direction: Direction
        :return: Nowa pozycja po przesunięciu.
        :rtype: Tuple[Decimal, Decimal]
        """
        if direction == Direction.LEFT:
            return (origin[0] - steps, origin[1])
        elif direction == Direction.RIGHT:
            return (origin[0] + steps, origin[1])
        elif direction == Direction.UP:
            return (origin[0], origin[1] - steps)
        elif direction == Direction.DOWN:
            return (origin[0], origin[1] + steps)

    def load_maze(self, file_path: str):
        """Ładuje labirynt z pliku.
        Metoda ignoruje białe znaki w pliku.
        :param file_path: Ścieżka do pliku z danymi labiryntu.
        :type file_path: str
        """
        from .maze_object import MazeObject

        lines = []
        pos = [0,0]
        with open(file_path, 'r') as file:
            lines = file.readlines()
            self.size = (len(lines[0]), len(lines))  # Zakłada, że wszystkie linie mają tę samą długość
            for line in lines:
                # Usuwanie białych znaków z linii
                line = line.strip()
                pos[0] = 0
                for char in line:
                    MazeObject.create_obj_based_on_char(char, tuple(pos), self)
                    pos[0] += 1
                pos[1] += 1


    
    def get_all_objects(self) -> List:
        """Zwraca listę wszystkich obiektów znajdujących się w labiryncie.

        :return: Lista wszystkich obiektów w labiryncie.
        :rtype: List[MazeObject]
        """
        
        return self.objects_at.values()

    def get_objects_at(self, pos : Tuple[int,int]):
        """Zwraca zbiór obiektów znajdujących się w danym miejscu labiryntu.

        :param pos: Pozycja w labiryncie, z której chcemy pobrać obiekty.
        :type pos: Tuple[int, int]
        :return: zbiór obiektów znajdujących się w danym miejscu labiryntu.
        :rtype: Set[MazeObject]
        """
        
        return self.objects_at.get(pos, set())
    
    def check_wall(self, pos: Tuple[int, int]) -> bool:
        """Sprawdza, czy w danej pozycji znajduje się ściana.

        :param pos: Pozycja do sprawdzenia.
        :type pos: Tuple[int, int]
        :return: True jeśli w danej pozycji znajduje się ściana, False w przeciwnym razie.
        :rtype: bool
        """
        from src.pacman.maze.objects import Wall
        objs : Set = self.objects_at.get(pos, set())
        for obj in objs:
            if isinstance(obj, Wall):
                return True
        return False
    
    def get_size(self) -> Tuple[int, int]:
        """Zwraca rozmiar labiryntu.

        :return: Rozmiar labiryntu w postaci krotki (szerokość, wysokość).
        :rtype: Tuple[int, int]
        """
        return self.size
    
    def to_csv_line(self) -> List[str]:
        """Zwraca reprezentację labiryntu w formacie CSV.

        :return: Reprezentacja labiryntu w formacie CSV.
        :rtype: List[str]
        """
        ret = []

        for obj in self.objects_at.values():
            ret += obj.to_cvs_line()
    
    def get_csv_header(self) -> List[str]:
        """Zwraca nagłówek CSV dla labiryntu.

        :return: Nagłówek CSV.
        :rtype: List[str]
        """
        ret = []

        for obj in self.objects_at.values():
            ret += obj.get_csv_header()

    def _add_object(self, obj):
        """Funkcja służąca do aktualizacji stanu labiryntu po dodaniu nowego obiektu, bądź po zmianie pozycji istniejącego obiektu.
        Dodaje przypisanie obiektu do odpowiedniego pola.

        :param obj: Obiekt do wstawienia.
        :type obj: MazeObject
        """
        if obj.get_position() not in self.objects_at:
            self.objects_at[obj.get_position()] = set()
        self.objects_at[obj.get_position()].add(obj)

    def _remove_object(self, obj):
        """
        Funkcja służąca do aktualizacji stanu labiryntu po usunięciu obiektu, bądź po zmianie pozycji istniejącego obiektu.
        Usuwa przypisanie obiektu z odpowiedniego pola.

        :param obj: Obiekt do usunięcia z labiryntu.
        :type obj: MazeObject
        """
        self.objects_at[obj.get_position()].remove(obj)
    
    def get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Zwraca listę sąsiadujących pozycji w labiryncie.

        :param pos: Pozycja, dla której chcemy znaleźć sąsiadów.
        :type pos: Tuple[int, int]
        :return: Lista sąsiadujących pozycji.
        :rtype: List[Tuple[int, int]]
        """
        
        neighbors = [
            (pos[0] - 1, pos[1]),   # Lewa
            (pos[0] + 1, pos[1]),   # Prawa
            (pos[0], pos[1] - 1),   # Góra
            (pos[0], pos[1] + 1)    # Dół
        ]
        
        return [n for n in neighbors if not self.check_wall(n)]
    
    def is_intersection(self, pos: Tuple[Decimal, Decimal]) -> bool:
        """Sprawdza, czy dana pozycja jest przecięciem w labiryncie.
        UWAGA: Gra nie sprawdza czy pozycje wychodzą poza labirynt, takie zachowanie jest konieczne dla wsparcia portali. Ściany wokół mapy powinny być wystarczające.

        :param pos: Pozycja do sprawdzenia.
        :type pos: Tuple[Decimal, Decimal]
        :return: True jeśli pozycja jest przecięciem, False w przeciwnym razie.
        :rtype: bool
        """
        if self.check_wall(pos):
            return False

        check_positions = [
            (pos[0] - 1, pos[1]),   # Lewa
            (pos[0] + 1, pos[1]),   # Prawa
            (pos[0], pos[1] - 1),   # Góra
            (pos[0], pos[1] + 1)    # Dół)
        ]
        # jedyne przypadki w których to nie jest przecięcie to: 0011 oraz 1100
        walls = [self.check_wall(p) for p in check_positions]

        if walls == [False, False, True, True] or walls == [True, True, False, False]:
            return False
        return True
