from matplotlib.figure import Figure
from src.pacman.maze_utils import MazeUtils
from src.pacman.game_state import GameState
from src.general import AGameStatsDisplay
from matplotlib.pyplot import plot
class StatsDisplay(AGameStatsDisplay):
    
    def __init__(self, fig = Figure(figsize=(20, 10), dpi=70)):
        super().__init__(fig, window_geometry='1400x600', redraw_interval=2000)
        self.prev_score = 0
        self.maze_utils : MazeUtils = None
        self.ai_bonuses = []

    def gather_stats(self, state : GameState):
        """Metoda wywoływana przy każdym kroku gry. Wyświetla statystyki gry."""
        score = state.score
        
        if state.is_game_over: 
            self.add_new_score(self.prev_score)
            self.ai_bonuses.append(state.ai_bonus)
            self.prev_score = 0
        self.prev_score = score

    def redraw(self):
        ax_score = self.figure.add_subplot(1, 2, 1)
        ax_graph = self.figure.add_subplot(1, 2, 2)
        self.plot_score(ax_score)
        self.maze_utils.draw(ax_graph)

    def plot_score(self, ax):

        super().plot_score(ax)
        x = list(range(1, len(self.ai_bonuses) + 1))

        penalties = []
        bonuses = []

        for score in self.ai_bonuses:
            bonus = 0
            penalty = 0

            if score > 0: bonus = score
            elif score < 0: penalty = -score

            bonuses.append(bonus)
            penalties.append(penalty)

        ax.plot(x, bonuses, label='Bonusy AI', linestyle='--')
        ax.plot(x, penalties, label='Kary AI', linestyle='--')

        ax.legend()


        