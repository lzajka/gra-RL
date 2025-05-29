from src.snake.agents.default import player
from src.snake.game_state import GameState
from typing import Tuple

class Player(player.Player):
    def __init__(self, args):
        super().__init__(args)
    
    def count_number_of_free_cells_in_box(self, state : GameState, tl : Tuple[int, int], br: Tuple[int, int]):
        """Metoda służy do obliczenia

        Args:
            state (GameState): Stan gry
            tl (Tuple[int, int]): Lewy górny róg
            br (Tuple[int, int]): Dolny prawy róg
        """

        free_cells = 0
        for i in range(tl[0], br[0] + 1):
            for j in range(tl[1], br[1] + 1):
                if (i, j) not in state.snake_tail_set and (i, j) != state.snake_position:
                    free_cells += 1
        return free_cells

    def detect_danger(self, state):
        """Override metody rodzica w sposób taki, aby snake mógł wykryć czy konkretny ruch nie doprowadzi go do sytuacji, w której snake na dobre ograniczy sobie pole manewru.

        Args:
            state (GameState): Aktualny stan gry.
        """

        danger_super = super().detect_danger(state)