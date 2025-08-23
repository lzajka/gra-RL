import src.general.agame_stats_display as AGameStats
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from IPython import display
from src.pacman.game_state import GameState
from src.pacman.maze_utils import MazeUtils


class GameStatsDisplay(AGameStats.AGameStatsDisplay):
    """
    Klasa GameStats dziedziczy po klasie AGameStats i implementuje metodę on_next_frame,
    która jest wywoływana przy każdym kroku gry. 
    """

    def __init__(self, fig = Figure(figsize=(15, 10))):
        super().__init__(fig)
        self.prev_score = 0
        self.maze_utils : MazeUtils = None

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

        