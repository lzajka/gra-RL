from .actor import Actor
from src.general.direction import Direction
from src.general.maze import Maze
from src.pacman.game_core import GameCore
from decimal import Decimal

class Pacman(Actor):
    """Klasa reprezentująca Pacmana, dziedzicząca po klasie Actor.
    Pacman jest aktorem, który porusza się po labiryncie i zbiera punkty.
    """

    def __init__(self, maze : Maze, respawn_interval: int = 0):
        super().__init__(maze, respawn_interval, "Pacman", (0,0))
        self.prepicked_direction = Direction.RIGHT
        Pacman.main_instance = self

    @classmethod 
    def get_instance(cls):
        """Zwraca instancję Pacmana
        """
        return cls.main_instance
    
    def get_status_effect_speed_modifier(self, state, level):
        from src.pacman.actors import SpeedStatusEffect
        if level == 1:
            if state == SpeedStatusEffect.NORM: return Decimal('0.8')
            elif state == SpeedStatusEffect.FRIGHT: return ('0.9')
            elif state == SpeedStatusEffect.TUNNELING: return Decimal('0.4')
        elif 2 <= level <= 4:
            if state == SpeedStatusEffect.NORM: return Decimal('0.9')
            elif state == SpeedStatusEffect.FRIGHT: return Decimal('0.95')
            elif state == SpeedStatusEffect.TUNNELING: return None
        elif 5 <= level <= 20:
            if state == SpeedStatusEffect.NORM: return Decimal('1')
            elif state == SpeedStatusEffect.FRIGHT: return Decimal('1')
            elif state == SpeedStatusEffect.TUNNELING: return None
        else:
            if state == SpeedStatusEffect.NORM: return Decimal('0.9')
            elif state == SpeedStatusEffect.FRIGHT: return None
            elif state == SpeedStatusEffect.TUNNELING: return None

    def copy(self):
        return None
    
    def get_target(self):
        """Zwraca cel, do którego Pacman ma się udać.
        W przypadku Pacmana jest to pozycja, o 1 krok w kierunku, w którym aktualnie się porusza.
        
        :return: Pozycja celu w postaci krotki (x, y).
        :rtype: Tuple[int, int]
        """
        pos = self.get_position()
        if self.direction == Direction.LEFT:
            self.target = (pos[0] - 1, pos[1])
        elif self.direction == Direction.RIGHT:
            self.target = (pos[0] + 1, pos[1])
        elif self.direction == Direction.UP:
            self.target = (pos[0], pos[1] - 1)
        elif self.direction == Direction.DOWN:
            self.target = (pos[0], pos[1] + 1)
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
        return super().on_game_update(current_state)
    
    def toggle_tunnel(self):
        pass
    

    
        
    
        

