from src.general import AGameCore, AGameState
from .game_config import GameConfig
from .game_state import GameState
from copy import deepcopy
from src.general import Direction
from src.pacman.maze import Maze
from queue import Queue
import pygame

class GameCore(AGameCore):
    _main_instance = None
    def __init__(self):
        self.config = self.get_default_config()

        super().__init__(self.config.WINDOW_DIMENSION, [
            'background',
            'map',
            'fruits',
            'actors'
        ])
        self.fps_controller = pygame.time.Clock()
        if self.__class__._main_instance is not None:
            raise RuntimeError('Tylko jedna instancja gry może istnieć w danym czasie.')
        self.__class__._main_instance = self
        self.maze : Maze = None
        self.current_state : GameState = None


    @classmethod
    def get_main_instance(cls):
        """Zwraca główną instancję gry."""
        return cls._main_instance

    def quit():
        pygame.quit()

    def get_game_config(self):
        """Zwraca aktualną konfigurację gry."""
        return self.config

    def on_make_move(self, move : Direction):
        from .actors.pacman import Pacman
        '''Metoda wykonywana przy podjęciu ruchu przez gracza. To nadpisanie umożliwia wykonanie przyłączonych do `next_frame_hooks` funkcji.
        
        :param move: Ruch gracza.
        :type move: Direction
        :return: Stan gry po wykonaniu ruchu.
        :rtype: GameState
        '''

        # Przed
        self.prev_state = self.current_state.copy()
        # Po
        # Przekaż pacmanowi ruch
        Pacman.get_instance().set_direction(move)
        self._run_hooks()
        self.render()
        self.fps_controller.tick(self.current_state.fps)
        #self.game_state.events = pygame.event.get()

        return self.current_state
    
    def _run_hooks(self):
        """Uruchamia wszystkie zarejestrowane funkcje przy każdym kroku gry."""
        hooks = self.next_frame_hooks.copy()
        for hook in hooks:
            if hook is not None:
                hook(self.current_state)
    
    def get_grid_cell_size(self):
        """Zwraca rozmiar komórki siatki w pikselach."""
        if self.cell_size is None:
            # Ponieważ self.maze jeszcze nie jest ustawione, wykorzystam Maze.get_main_instance()

            self.cell_size = self.config.WINDOW_DIMENSION[0] // Maze.get_main_instance().get_size()[0]
        return self.cell_size

    def get_current_state(self):
        """Zwraca aktualny stan gry."""
        return self.current_state
    
    
    def on_restart(self, config):
        '''Metoda restartuję grę. Wykorzystuje podaną konfigurację. Zwraca stan gry
        :param config: Konfiguracja gry.
        :type config: GameConfig
        :return: Stan gry po restarcie.
        :rtype: GameConfig
        '''
        if config is None:
            config = GameConfig()
        self.config = config
        self.next_frame_hooks = []
        self.free_hooks = Queue()
        self.fill_layer('background', (0,0,0))


        
        # Inicjalizacja labiryntu
        self.cell_size = None
        self.maze = Maze()
        self.maze.load_maze(self.config.MAZE_FILE)
        self.current_state = GameState(self.maze, self.config.STARTING_LIVES)
        
        return self.current_state

    def register_frame_hook(self, hook) -> int:
        """Rejestruje funkcję, która zostanie wywołana przy każdym kroku gry.
        
        :param hook: Funkcja, która zostanie wywołana przy każdym kroku gry.
        :type hook: Callable
        :raises TypeError: Jeśli hook nie jest funkcją.
        :return: Indeks, pod którym funkcja została zarejestrowana.
        :rtype: int
        """
        if not callable(hook):
            raise TypeError('Hook musi być funkcją.')
        
        if not self.free_hooks.empty():
            hook_id = self.free_hooks.get()
        else:
            self.next_frame_hooks.append(None)
            hook_id = len(self.next_frame_hooks) - 1
        
        self.next_frame_hooks[hook_id] = hook
        return hook_id

    def unregister_frame_hook(self, hook_id : int) -> None:
        """Usuwa funkcję z listy funkcji wywoływanych przy każdym kroku gry.

        :param hook: _description_
        :type hook: _type_
        """

        if hook_id < 0 or hook_id >= len(self.next_frame_hooks):
            raise IndexError('Nieprawidłowy indeks hooka.')

        if self.next_frame_hooks[hook_id] is None:
            raise ValueError('Hook o podanym indeksie nie jest zarejestrowany.')
        self.next_frame_hooks[hook_id] = None
        self.free_hooks.put(hook_id)

    def get_default_config(self):
        return GameConfig()