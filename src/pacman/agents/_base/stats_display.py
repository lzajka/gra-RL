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
        self.bonuses = []

    def gather_stats(self, state : GameState):
        """Metoda wywoływana przy każdym kroku gry. Wyświetla statystyki gry."""
        score = state.score
        
        if state.is_game_over: 
            self.add_new_score(self.prev_score)
            self.bonuses.append((state.ai_bonus, state.move_num))
            self.prev_score = 0
        self.prev_score = score

    def redraw(self):
        ax_score = self.figure.add_subplot(1, 2, 1)
        ax_graph = self.figure.add_subplot(1, 2, 2)
        self.plot_score(ax_score)
        self.maze_utils.draw(ax_graph)

    def plot_score(self, ax):

        super().plot_score(ax)
        x = list(range(1, len(self.bonuses) + 1))

        round_bonuses = []
        round_penalties = []
        average_penalties = []
        average_bonuses = []

        for (round_score, move_num) in self.bonuses:
            round_bonus = 0
            round_penalty = 0
            average_bonus = 0
            average_penalty = 0

            if round_score >= 0: round_bonus = round_score
            else: round_penalty = -round_score

            average_bonus = round_bonus/move_num
            average_penalty = round_penalty/move_num

            round_bonuses.append(round_bonus)
            round_penalties.append(round_penalty)
            average_bonuses.append(average_bonus)
            average_penalties.append(average_penalty)


        ax.plot(x, average_bonuses, label='Bonusy AI/tick', color='green', linestyle='--')
        ax.plot(x, round_bonuses, label='Bonusy AI', color='green')
        ax.plot(x, average_penalties, label='Kary AI/tick', color='red', linestyle='--')
        ax.plot(x, round_penalties, label='Kary AI', color='red')

        ax.legend()


        