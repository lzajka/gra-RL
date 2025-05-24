from matplotlib import pyplot as plt
from IPython import display

from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib as mpl
from abc import ABC, abstractmethod
from numbers import Number
from src.general.agame_state import AGameState
from tkinter import Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from time import time_ns

class AGameStatsDisplay(ABC):

    """Abstrakcyjna klasa do wyświetlania statystyk gry.

    Zawiera metody 
    """

    def __init__(self, fig = Figure(figsize=(15, 10)), redraw_interval = 5000):
        """Konstruktor klasy AGameStats. Inicjalizuje zmienne do przechowywania wyników gry."""


        self.best_scores = []
        self.average_scores = []
        self.score_sum = 0
        self.scores = []
        self.figure = fig
        self.redraw_interval = redraw_interval 
        self.last_redraw = 0
        self.setup_window()

        
        
    def setup_window(self, window_geometry = '800x600'):
        """Metoda do ustawiania okna GUI. Ustawia rozmiar okna i inne parametry."""
        self.window = Tk()
        self.window.title('Panel')
        self.window.geometry(window_geometry)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.window)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)

    @abstractmethod
    def gather_stats(self, state : AGameState):
        """Metoda odpowiedzialna za zbieranie statystyk. Nie powinna być wywoływana bezpośrednio, po to jest metoda `update`.
        Klasa dziedzicząca **musi** zaimplementować tę metodę.

        :param state: Zmienna przechowująca stan gry.
        :type state: AGameState
        """
        pass

    def update(self, stats = {}):
        """Metoda aktualizująca. Wywołuje metodę `on_next_state`.

        :param state: Zmienna przechowująca stan gry.
        :type state: AGameState
        """
        self.gather_stats(stats)
        time_ms = time_ns() / int(1e6)

        if time_ms - self.last_redraw >= self.redraw_interval:
            self.redraw()
            
            self.canvas.draw()
            self.window.update()

            self.figure.clear()
            self.last_redraw = time_ns() / int(1e6)

    @abstractmethod
    def redraw(self):
        """Metoda rysująca statystyki. 
        Wywoływana jest przy każdym kroku gry, co `redraw_interval` milisekund.
        """
        pass
    




    def add_new_score(self, score : Number):
        """Metoda do dodawania nowego wyniku.

        :param score: Nowy wynik do dodania do statystyk.
        :type scores: Number
        """

       
        self.scores.append(score)
        score_count = len(self.scores)


        # Najlepszy wynik
        prev_score = -99999999 if len(self.best_scores) == 0 else self.best_scores[-1]
        self.best_scores.append(max(prev_score, score))
        

        # Średni wynik
        self.score_sum += score
        self.average_scores.append(self.score_sum / score_count)
        
        
    def plot_score(self, ax : Axes) -> Axes:
        """Metoda do rysowania wykresu wyników.

        :param ax: Oś, na której ma być narysowany wykres.
        :type ax: Axes
        :return: Oś z narysowanym wykresem.
        :rtype: Axes
        """
        ax.clear()
        ax.set_xlabel('Liczba gier')
        ax.set_ylabel('Wynik')
        ax.set_title(f'Wyniki gry')
        ax.grid(True)

        score_count = len(self.scores)

        if score_count == 0:
            ax.text(0.5, 0.5, 'Brak wyników do wyświetlenia', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
            return ax

        x = list(range(1, score_count + 1))

        ax.plot(x, self.best_scores, label='Najlepszy wynik', color='blue')
        ax.plot(x, self.average_scores, label='Średni wynik', color='orange')
        ax.plot(x, self.scores, label='Aktualny wynik', color='green')

        ax.legend()
        ax.set_ylim(bottom=0)        
        return ax
