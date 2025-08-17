from src.pacman.game_core import GameCore
from src.pacman.game_state import GameState
__all__ = [
    "start_frame_timer",
    "start_time_timer",
    "cancel_timer"
]

_timer_mappings = []                                        # Tablica przypisująca każdemu timerowi id frame hooka
_freed_mappings = []                                        # Aby tablica nierosła w nieskończoność
_timer_priorities = []

def _fexecutor(game_state : GameState, func, frame_number, timer_id):
    if game_state.frame >= frame_number:
        func(game_state)
        cancel_timer(timer_id)



def _texecutor(game_state : GameState, func, time_elapsed, timer_id):
    if game_state.time_elapsed >= time_elapsed:
        func(game_state)
        cancel_timer(timer_id)



def _get_timer_id():
    global _freed_mappings, _timer_mappings, _timer_priorities
    if len(_freed_mappings) > 0:
        return _freed_mappings.pop(0)
    else:
        _timer_mappings.append(None)                # Dodajemy nowy timer
        _timer_priorities.append(None)
        return len(_timer_mappings) - 1
    
def cancel_timer(timer_id):
    global _timer_mappings, _timer_priorities
    hook_id = _timer_mappings[timer_id] if timer_id < len(_timer_mappings) else None
    priority = _timer_priorities[timer_id] if timer_id < len(_timer_priorities) else None

    if hook_id is None:
        raise ValueError(f"Timer z id {timer_id} nie istnieje, lub został usunięty.")

    GameCore.get_main_instance().unregister_frame_hook(hook_id, priority)

    # Oznaczamy jako usunięty
    _timer_mappings[timer_id] = None
    _timer_priorities[timer_id] = None
    _freed_mappings.append(timer_id)

def start_frame_timer(frames, func, priority = 0) -> int:
    """Uruchamia timer, wywołuje on po upływie określonej ilości ramek funkcję.

    :param frames: Ilość ramek do odczekania przed wywołaniem funkcji.
    :type frames: int
    :param priority: Priorytet timera.
    :type priority: int
    :param func: Funkcja do wykonania po upływie czasu.
    :type func: Callable
    """
    global _timer_mappings
    current_frame = GameCore.get_main_instance().get_current_state().frame
    timer_id = _get_timer_id()

    hook_id = GameCore.get_main_instance().register_frame_hook(
        lambda game_state : _fexecutor(game_state, func, current_frame + frames, timer_id),
        priority)
    
    _timer_mappings[timer_id] = hook_id
    _timer_priorities[timer_id] = priority

def start_time_timer(seconds, func, priority = 0) -> int:
    """Uruchamia timer, wywołuje on po upływie określonego czasu funkcję.

    :param seconds: Ilość sekund do odczekania przed wywołaniem funkcji.
    :type seconds: float
    :param priority: Priorytet timera.
    :type priority: int
    :param func: Funkcja do wykonania po upływie czasu.
    :type func: Callable
    """
    global _timer_mappings
    current_time = GameCore.get_main_instance().get_current_state().time_elapsed

    timer_id = _get_timer_id()

    hook_id = GameCore.get_main_instance().register_frame_hook(
        lambda game_state : _texecutor(game_state, func, current_time + seconds, timer_id),
        priority)

    _timer_mappings[timer_id] = hook_id
    _timer_priorities[timer_id] = priority

from src.general import reload_functions
def _reload():
    global _timer_mappings, _freed_mappings, _timer_priorities
    _timer_mappings = []
    _freed_mappings = []
    _timer_priorities = []
    
reload_functions.append(_reload)