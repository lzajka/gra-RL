from .actor import Actor
from src.general.direction import Direction
from src.pacman.maze import Maze
from src.pacman.game_core import GameCore

class Pacman(Actor):
    """Klasa reprezentująca Pacmana, dziedzicząca po klasie Actor.
    Pacman jest aktorem, który porusza się po labiryncie i zbiera punkty.
    """

    def __init__(self, maze : Maze, respawn_interval: int = 0):
        super().__init__(maze, respawn_interval, "Pacman", (0,0))
        Maze.get_main_instance().pacman = self
        self.prepicked_direction = Direction.RIGHT
        
    
    @classmethod
    def get_instance(cls):
        """Zwraca instancję Pacmana.
        
        :return: Instancja Pacmana.
        :rtype: Pacman
        """
        from src.pacman.maze import Maze
        return Maze.get_main_instance().pacman
    

    def copy(self):
        return None
    
    def get_target(self):
        """Zwraca cel, do którego Pacman ma się udać.
        W przypadku Pacmana jest to pozycja, o 1 krok w kierunku, w którym aktualnie się porusza.
        
        :return: Pozycja celu w postaci krotki (x, y).
        :rtype: Tuple[int, int]
        """

        if self.direction == Direction.LEFT:
            self.target = (self.position[0] - 1, self.position[1])
        elif self.direction == Direction.RIGHT:
            self.target =(self.position[0] + 1, self.position[1])
        elif self.direction == Direction.UP:
            self.target = (self.position[0], self.position[1] - 1)
        elif self.direction == Direction.DOWN:
            self.target = (self.position[0], self.position[1] + 1)
        return self.target

    
    def set_direction(self, direction: Direction):
        """Ustawia kierunek ruchu Pacmana.
        
        :param direction: Kierunek, w którym Pacman ma się poruszać.
        :type direction: Direction
        """
        if direction is not None:
            self.prepicked_direction = direction
    
    def on_intersection(self):
        prev_dir = self.direction
    
        self.direction = self.prepicked_direction

        # Sprawdz czy taki mozna
        # 1. Sprawdz czy obrot o 180
        if prev_dir.opposite() == self.direction:
            # Nie mozna, wiec nie zmieniaj kierunku
            self.direction = prev_dir
        # 2. Sprawdz czy mozna w ogole w tym kierunku isc
        elif self.maze.check_wall(self.get_target()):
        # Jeżeli nie można, to nie zmieniaj kierunku
            self.direction = prev_dir
        
    def get_csv_header(self):
        return ['PacmanPosX', 'PacmanPosY', 'PacmanDirection']

    def to_csv_line(self):
        return [
            str(self.position[0]),
            str(self.position[1]),
            self.direction.name
        ]

    def _get_filled_ratio(self):
        return GameCore.get_main_instance().get_game_config().ACTOR_FILLED_RATIO
    
    def _get_color(self):
        return GameCore.get_main_instance().get_game_config().PACMAN_COLOR
    
    def _get_named_layer(self):
        return 'actors'
    
    def on_game_update(self, current_state):
        self.check_collision(self.get_position())
        return super().on_game_update(current_state)
    
    def check_collision(self, position):
        """
        Metoda ta jest wywoływana co każdą klatkę gry, aby sprawdzić, czy Pacman zderzył się z jakimś obiektem.
        :param position: Pozycja, z którą Pacman ma sprawdzić kolizję.
        :type position: tuple[int, int]
        """
        from src.pacman.maze import point
        from src.pacman.game_state import GameState
        gs = GameState.get_main_instance() 

        objs = self.maze.get_objects_at(position)
        to_destroy = []
        if objs is not None:
            for obj in objs:
                if isinstance(obj, point.Point):
                    gs.score += 1
                    gs.collected_points += 1
                    to_destroy.append(obj)

        for obj in to_destroy:
            obj.destroy()
    

    
        
    
        

