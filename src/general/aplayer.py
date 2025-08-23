from abc import ABC, abstractmethod
from csv import writer
from argparse import ArgumentParser

class APlayer(ABC):
    from src.general.agame_core import AGameCore
    from src.general.agame_state import AGameState

    def __init__(self, args : ArgumentParser, config_overrides : dict = {}):
        """Konstruktor klasy APlayer. Klasa ta jest klasą bazową dla wszystkich graczy. Klasa ta nie powinna być używana bezpośrednio.

        :param args: Argumenty linii poleceń.
        :type args: ArgumentParser
        :param config_overrides: Mapa nadpisująca konfiguracje, wyrażona jako słownik. Kluczami są nazwy parametrów, a wartościami są nowe wartości parametrów. Jeżeli nie podano, używane są domyślne wartości.
        :type config_overrides: dict, optional
        :raises Exception: Błąd podczas otwierania pliku.
        """
        self.game = self.getGame()
        self.file = None
        self.csv = None
        self.round_number = 0
        self.move_number = 0
        self.prev_state_copy = True

        stats_path = args.output_stats

        # Sprawdź czy plik został poprawnie otwarty, jeżeli nie zgłoś wyjątek
        if stats_path is not None:
            self.file = open(stats_path, 'w')
            if self.file.closed:
                raise Exception(f'Nie można otworzyć pliku {stats_path}')
            self.csv = writer(self.file)
            self.header_written = False

        # Nadpisz konfigurację
        self.game_config = self.game.get_default_config()
        self.game_config = self.handle_config_overrides(self.game_config, config_overrides)

    @abstractmethod
    def getGame(self) -> AGameCore:
        """Funkcja tworząca instancję gry. Wywoływana podczas inicjalizacji gracza.

        :return: Utworzona instancja gry.
        :rtype: AGameCore
        """
        pass

    def handle_config_overrides(self, default_config, overrides : dict):
        """Funkcja do obsługi nadpisania konfiguracji. Funkcja ta jest wywoływana przed rozpoczęciem gry.

        Args:
            overrides (dict): Słownik z parametrami do nadpisania.
        """
        for key, value in overrides.items():
            if hasattr(default_config, key):
                
                setattr(default_config, key,type(getattr(default_config, key))(value))
                
            else:
                raise KeyError(f'Nieznany klucz {key} w konfiguracji.')
        return default_config
    
    def can_make_a_decision(self, state):
        return True

    def prepare_env(self, state):
        return state

    def fast_forward(self, state : AGameState) -> AGameState:
        while not self.can_make_a_decision(state) and not state.is_game_over:
            state = self.game.make_move(None)
            self.on_update(state)
        return state
    
    def visit_state(self, state : AGameState):
        """Metoda wykorzystywana do zebrania informacji o stanie. i-te wywołanie to i-ty stan.

        :param state: _description_
        :type state: AGameState
        """
        pass

    def on_update(self, state : AGameState):
        pass

    def play(self, config = None):
        is_running = True
        config = self.game_config
        while is_running:
            old_state = None
            # Zresetuj grę i wczytaj stan początkowy
            state = self.game.restart(config)
            state = self.prepare_env(state)
            self.on_update(state)
            state = self.fast_forward(state)
            self.visit_state(state)

            # Zapisz stan do pliku
            self.write_stats(state)
            
            # Jeżeli doszło do końca gry to 
            while not state.is_game_over and is_running:

                # Zapisz stary stan
                if self.prev_state_copy: old_state = state.copy()

                # Podejmij decyzję
                [player_move, is_running] = self.make_decision(state)
                
                # Wykonaj działania związane z podjęciem decyzji
                if not is_running: break
                self.on_decision_made(state, player_move)
                
                # Przejdź do następnego decydującego stanu gry
                state = self.game.make_move(player_move)
                self.on_update(state)
                state = self.fast_forward(state)
                self.visit_state(state)

                # Wykonaj akcje związane z nowym stanem
                self.on_move_made(old_state, state, player_move)

                # Zapisz info stanu
                self.write_stats(state)

                # Inkrementuj ruch
                self.move_number += 1

            self.on_game_over(state)
            # Zwiększ numer rundy
            self.round_number += 1
            self.move_number = 0
        self.quit()
    @abstractmethod
    def make_decision(self, state : AGameState):
        pass

    def write_stats(self, state : AGameState):
        """Funkcja zapisuje statystyki do pliku podanego podczas tworzenia obiektu. Jeżeli plik nie został podany, funkcja nic nie robi. Funkcja ta jest wywoływana po zakończeniu rundy.
        Zapisywane dane pochodzą ze stanu gry oraz innych danych takich jak numer ruchu, czy numer rundy.

        Args:
            stats (AGameState): Stan gry do zapisania.
        """
        if self.csv is None:
            return
        
        additional_headers = ['runda', 'ruch']
        additional_values = [self.round_number, self.move_number]

        # Jeżeli jeszcze nie zapisano nagłówków, zapisz je
        if not self.header_written:
            self.csv.writerow(additional_headers + state.get_headers())
            self.header_written = True

        # Zapisz stan gry
        self.csv.writerow(additional_values + state.to_list())
        

    def quit(self):
        self.on_quit()
        if self.file is not None: self.file.close()
        from pygame import quit
        quit()

    def on_quit(self):
        """Event handler wywoływany po zakończeniu gry.
        """
        pass

    def on_game_over(self, state : AGameState):
        """Event handler wywoływany w momencie zakończenia rundy. Jeżeli potrzebne jest wykorzystanie statystyk, należy je zebrać podczas on_decision_made.

        Args:
            state (AGameState): Stan gry
        """
        pass

    def on_decision_made(self, state : AGameState, player_move):
        """Event handler wywoływany po podjęciu decyzji przez gracza. Pozwala na zbieranie statystyk związanych z grą.

        Args:
            state (AGameState): Stary gry.
            player_move (Any): Ruch gracza.
        """
        pass

    def on_move_made(self, old_state : AGameState, new_state : AGameState, player_move):
        """Event handler wywoływany po wykonaniu ruchu przez gracza. Pozwala na zbieranie statystyk związanych z grą.

        Args:
            old_state (AGameState): Stary stan gry.
            new_state (AGameState): Nowy stan gry.
            player_move (Any): Ruch gracza.
        """
        pass