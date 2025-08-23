from src.general import AGameCore, AGameState
from .game_config import GameConfig
from .game_state import GameState
from copy import deepcopy
from src.general import Direction
from src.general.maze import Maze, UsesMaze
from queue import Queue
import pygame
from .ghost_schedule import GhostSchedule
HOOK_PRIORITY_COUNT = 10

class GameCore(AGameCore, UsesMaze):
    _main_instance = None
    

    def __init__(self):

        import src.pacman.maze.objects
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
        GameCore.maze : Maze = None
        self.game_state : GameState = None
        self._ghost_schedule = None

    @classmethod
    def get_maze(cls):
        return cls.maze

    @classmethod
    def get_main_instance(cls) -> 'GameCore':
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
        pacman : Pacman = Pacman.get_instance(self.game_state)
        pacman.set_direction(move)
        if self.game_state.schedule is None:
            raise RuntimeError('Nie ustawiono harmonogramu duchów. Ustaw harmonogram za pomocą metody `set_level` przed wykonaniem ruchu.')
        self._run_hooks()
        GameCore.get_main_instance().show_score()
        self.render()
        
        self.fps_controller.tick(self.fps)
        time_delta = 1.0/self.fps
        self.game_state.frame += 1
        self.game_state.time_elapsed += time_delta
        self.game_state.schedule.add_time(time_delta)
        #self.game_state.events = pygame.event.get()

        return self.game_state
    
    def _run_hooks(self):
        """Uruchamia wszystkie zarejestrowane funkcje przy każdym kroku gry."""
        hooks = sum(self.next_frame_hooks, [])
        for hook in hooks:
            if hook is not None:
                hook(self.game_state)
    
    def get_grid_cell_size(self):
        """Zwraca rozmiar komórki siatki w pikselach."""
        if self.cell_size is None:
            # Ponieważ self.maze jeszcze nie jest ustawione, wykorzystam Maze.get_main_instance()

            self.cell_size = self.config.WINDOW_DIMENSION[0] // self.maze.get_size()[0]
        return self.cell_size

    def get_current_state(self):
        """Zwraca aktualny stan gry."""
        return self.game_state
    
    def on_restart(self, config):
        '''Metoda restartuję grę. Wykorzystuje podaną konfigurację. Zwraca stan gry
        :param config: Konfiguracja gry.
        :type config: GameConfig
        :return: Stan gry po restarcie.
        :rtype: GameConfig
        '''
        from src.general import reload_all
        reload_all()
        if config is None:
            config = GameConfig()
        self.config = config
        self.fps = config.FRAME_RATE
        self.next_frame_hooks = []
        self.free_hooks = []
        

        for _ in range(HOOK_PRIORITY_COUNT):
            self.free_hooks.append(Queue())
            self.next_frame_hooks.append([])

        self.fill_layer('background', (0,0,0))


        
        # Inicjalizacja labiryntu
        self.cell_size = None
        self.game_state = GameState()
        self.game_state.maze = self.maze = Maze(self.game_state)
        self.maze.load_maze(self.config.MAZE_FILE)
        self.game_state.maze = self.maze
        self.game_state.round += 1
        
        return self.game_state

    def register_frame_hook(self, hook, priority_group=0) -> int:
        """Rejestruje funkcję, która zostanie wywołana przy każdym kroku gry.
        
        :param hook: Funkcja, która zostanie wywołana przy każdym kroku gry.
        :type hook: Callable
        :param priority_group: Grupa priorytetowa, do której należy funkcja. Funkcje o niższej wartości będą wywoływane wcześniej. Domyślnie 0.
        :type priority_group: int
        :raises TypeError: Jeśli hook nie jest funkcją.
        :raises IndexError: Jeśli grupa priorytetowa jest spoza zakresu.
        :return: Indeks, pod którym funkcja została zarejestrowana.
        :rtype: int
        """

        if priority_group < 0 or priority_group >= HOOK_PRIORITY_COUNT:
            raise IndexError('Nieprawidłowa grupa priorytetowa.')
        if not callable(hook):
            raise TypeError('Hook musi być funkcją.')
        
        if not self.free_hooks[priority_group].empty():
            hook_id = self.free_hooks[priority_group].get()
        else:
            self.next_frame_hooks[priority_group].append(None)
            hook_id = len(self.next_frame_hooks[priority_group]) - 1

        self.next_frame_hooks[priority_group][hook_id] = hook
        return hook_id

    def unregister_frame_hook(self, hook_id : int, priority_group: int) -> None:
        """Usuwa funkcję z listy funkcji wywoływanych przy każdym kroku gry.

        :param hook: Identyfikator funkcji, która ma zostać usunięta.
        :type hook: int
        :param priority_group: Grupa priorytetowa, do której należy funkcja.
        :type priority_group: int
        :raises IndexError: Jeśli indeks hooka jest spoza zakresu.
        :raises ValueError: Jeśli hook o podanym indeksie nie jest zarejestrowany.
        :raises IndexError: Jeśli grupa priorytetowa jest spoza zakresu.
        """

        if priority_group < 0 or priority_group >= HOOK_PRIORITY_COUNT:
            raise IndexError('Nieprawidłowa grupa priorytetowa.')
        
        hook_group = self.next_frame_hooks[priority_group]

        if hook_id < 0 or hook_id >= len(hook_group):
            raise IndexError('Nieprawidłowy indeks hooka.')

        if hook_group[hook_id] is None:
            raise ValueError('Hook o podanym indeksie nie jest zarejestrowany.')
        hook_group[hook_id] = None
        self.free_hooks[priority_group].put(hook_id)

    def get_default_config(self):
        return GameConfig()