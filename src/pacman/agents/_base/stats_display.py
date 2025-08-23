from matplotlib.figure import Figure
from src.pacman.game_state import GameState
from src.general import AGameStatsDisplay

class StatsDisplay(AGameStatsDisplay):
    
    def __init__(self, fig = Figure(figsize=(15, 10))):
        super().__init__(fig)
        self.prev_score = 0

    def gather_stats(self, state : GameState):
        """Metoda wywoływana przy każdym kroku gry. Wyświetla statystyki gry."""
        score = state.score
        
        if state.is_game_over: 
            self.add_new_score(self.prev_score)
            self.prev_score = 0
        self.prev_score = score

    def redraw(self):
        ax_score = self.figure.add_subplot(1, 1, 1)
        self.plot_score(ax_score)

        