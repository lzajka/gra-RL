from src.general.agame_state import AGameState
import vizdoom as vd
from typing import List


class GameState(AGameState):
    """Wrapper dla stanu gry ViZDoom

    :param AGameState: _description_
    :type AGameState: _type_
    """
    def __init__(self, state : vd.GameState = None):
        super().__init__()
        if state == None:
            return
        vars = state.game_variables
        self.score = vars[0]
        #self.labels : List[vd.Label] = state.labels
        self.frame = state.number


    def get_headers(self):
        return []
    
    def to_list(self):
        return []
    
    def copy(self):
        s = GameState()
        s.score = self.score
        #s.labels = self.labels.copy()
        s.frame = self.frame
        return s