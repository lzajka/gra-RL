from .actor import Actor
from src.general.direction import Direction
from src.general.maze import Maze
from src.pacman.game_core import GameCore
from decimal import Decimal
from src.pacman.game_config import GameConfig

class Pacman(Actor):
    """Klasa reprezentująca Pacmana, dziedzicząca po klasie Actor.
    Pacman jest aktorem, który porusza się po labiryncie i zbiera punkty.
    """

    def __init__(self, state : Maze, respawn_interval: int = 0, name = 'Pacman', spawn=(0,0), **kwargs):

        super().__init__(respawn_interval=respawn_interval, name=name, state=state, spawn=spawn, **kwargs)
        self.prepicked_direction = Direction.RIGHT
        gc = GameCore.get_main_instance()
        self._game_config : GameConfig = gc.get_game_config()

    
    def _get_speed_multiplier(self):
        level = self._state.level
        
        if level == 1:
            if self.is_frightened: return Decimal('0.9')
            else: return Decimal('0.8')
        elif 2 <= level <= 4:
            if self.is_frightened: return Decimal('0.95')
            else: return Decimal('0.9')
        elif 5 <= level <= 20:
            if self.is_frightened: return Decimal('1')
            else: return Decimal('1')
        else:
            return Decimal('0.9')

    
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
        self.direction = self.prepicked_direction
    
    def is_intersection(self, pos):
        return True

    
    def _handle_reverse_signal(self):
        return super()._handle_reverse_signal()
        
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
    

    
    def kill(self):
        """Zabija pacmana wywołując koniec gry.
        """
        self._state.score += self._game_config.DEATH_REWARD
        self._state.is_game_over = True
    
        

