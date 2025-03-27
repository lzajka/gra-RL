from abc import ABC, abstractmethod

class APlayer(ABC):
    from src.general.igame_core import IGameCore
    from src.general.agame_state import AGameState

    def __init__(self, game: IGameCore):
        self.game = game

    def play(self, config) -> int:
        is_running = True
        state = None
        while is_running:
            state = self.game.restart(config)
            [player_move, is_running] = self.make_decision(state)

            while is_running and not state.is_game_over:
                state = self.game.make_move(player_move)
                [player_move, is_running] = self.make_decision(state)
        
        self.game.quit()
        return state.score


    @abstractmethod
    def make_decision(self, state : AGameState):
        pass