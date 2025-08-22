from logging import getLogger

class GhostSchedule():
    def __init__(self, level):
        from src.pacman.actors import GhostState
        self._schedule_timer = 0
        self.is_timer_paused = False
        self._level = level
        self._logger = getLogger(__name__)

        self._order = [
            # Poziom 1
            [
                (GhostState.SCATTER, 7),
                (GhostState.CHASE, 20),
                (GhostState.SCATTER, 7),
                (GhostState.CHASE, 20),
                (GhostState.SCATTER, 5),
                (GhostState.CHASE, 20),
                (GhostState.SCATTER, 5),
                (GhostState.CHASE, float('inf'))
            ],
            # Poziom 2-4
            [
                (GhostState.SCATTER, 7),
                (GhostState.CHASE, 20),
                (GhostState.SCATTER, 7),
                (GhostState.CHASE, 20),
                (GhostState.SCATTER, 5),
                (GhostState.CHASE, 1033),
                (GhostState.SCATTER, 1.0/60),
                (GhostState.CHASE, float('inf'))
            ],
            # Poziom 5+
            [
                (GhostState.SCATTER, 7),
                (GhostState.CHASE, 20),
                (GhostState.SCATTER, 5),
                (GhostState.CHASE, 20),
                (GhostState.SCATTER, 5),
                (GhostState.CHASE, 1037),
                (GhostState.SCATTER, 1.0/60),
                (GhostState.CHASE, float('inf'))
            ]
        ]
        self._level_index = self._get_level_index(level)
        self._cache = (-1, 0, -1) #czas_start, czas_stop, index

    def _get_level_index(self, level : int) -> int:
        if level == 1:
            return 0
        elif level <= 4:
            return 1
        else:
            return 2
        
    def add_time(self, time_delta: float):
        """Metoda wykonywana podczas aktualizacji.

        :param time_delta: czas który upłynął pomiędzy ramkami.
        :type time_delta: float
        """
        if not self.is_timer_paused:
            self._schedule_timer += time_delta
            self._update_ghosts(self._schedule_timer)


        


    def _get_state(self, time : float):
        """Zwraca stan obowiązujący w danej chwili. Zwraca None jeżeli stan się nie zmienił.

        :param time: Czas w sekundach
        :type time: float
        """
        # Wybierz początek, użyj cacheu do usprawnienia
        cache_starttime, cache_stoptime, cache_index = self._cache
        lvl = self._level_index
        

        start_index = 0
        counter = 0

        if cache_starttime <= time < cache_stoptime:
            # W tym wypadku nic się nie zmienia
            return None
        elif cache_stoptime <= time:
            start_index = cache_index + 1
            counter = cache_stoptime
        else:
            raise RuntimeError('Niepoprawny stan harmonogramu. Czas startowy nie może być większy niż czas końcowy.')
        
        lvl = self._level_index
        schedule = self._order[lvl]

        index = 0
        for i in range(start_index, len(schedule)):
            # Zaczynamy z i które obowiązuje od czasu według counter
            state, duration = schedule[i]
            start = counter
            end = counter + duration
            if start <= time < end:
                self._cache = start, end, i
                return state
        else:
            raise RuntimeError(f'Niepoprawny stan harmonogramu. Nie znaleziono stanu dla czasu: {time}. Sprawdź, czy harmonogram jest poprawnie skonfigurowany.')    

    def _update_ghosts(self, time : float):
        """Aktualizuje stan duchów na podstawie poziomu i czasu.

        :param time: Czas w sekundach
        :type time: float
        """
        from src.pacman.actors import GhostState
        state : GhostState = self._get_state(time)

        is_chasing = None
        if state is None:
            return
        elif state in (GhostState.CHASE, GhostState.SCATTER):
            is_chasing = state == GhostState.CHASE
        else:
            raise ValueError(f'Niewłaściwy stan harmonogramu: {state}. Oczekiwano stanu CHASE lub SCATTER.')

        
        self._logger.info(f'{time:.2f}:Aktualizuję stan duchów na {state}')
        from src.pacman.actors import Ghost
        Ghost.set_state_for_all(is_chasing=is_chasing)

            