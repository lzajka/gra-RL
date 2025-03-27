class AGameState:
    
    from typing import List
    from pygame import event
    
    score : int = 0
    is_game_over : bool = False
    events : List[event.Event] = []
