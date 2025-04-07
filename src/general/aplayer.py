from abc import ABC, abstractmethod

class APlayer(ABC):
    from src.general.agame_core import AGameCore
    from src.general.agame_state import AGameState

    def __init__(self, game: IGameCore):
        self.game = game

    def play(self, config = None):
        is_running = True
        state = None
        while is_running:
            state = self.game.restart(config)
            [player_move, is_running] = self.make_decision(state)

            while is_running and not state.is_game_over:
                state = self.game.make_move(player_move)
                [player_move, is_running] = self.make_decision(state)
            
            self.on_game_over(state)
        self.game.quit()

    @abstractmethod
    def make_decision(self, state : AGameState):
        pass

    def on_game_over(self, state : AGameState):
        pass