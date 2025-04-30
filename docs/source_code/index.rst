Kod źródłowy
=========================
    

- `src/general/` - Katalog zawierające powszechnie używaną funkcjonalność w grach
   -  `agame_core.py` - Klasa abstrakcyjna. Prosty silnik na podstawie Pygame.
   -  `game_state.py` - Klasa abstrakcyjna. Przechowuje informacje o stanie gry.
   -  `aplayer.py` - Klasa abstrakcyjna. Odpowiedzialna, za sterowanie.


============
Diagram klas
============



.. uml::

    abstract class AGameCore {
        + restart(config) : AGameState
        + make_move(move) : Tuple[AGameState, bool]
        + quit() : None
        + display_text(position : Tuple[int, int], text, font_size, font, color, background) : None
        + clear_text(position : Tuple[int, int]) : None
        + draw_box(pos : [int, int] , color, cell_size = None) : None
        + show_score() : None
        + render() : None
        + {abstract} quit() : None
        + {abstract} on_make_move(move) : None
        + {abstract} on_restart(config) : None
        + {abstract} get_default_config() : GameConfig
        - __render_text(position : Tuple[int, int]) : None
        - __render_texts() : None
    }

    abstract class AGameState {
        + score : int
        + is_game_over : bool
        + events : List[event.Event]
        + {abstract} to_list() : List[str]
        + {abstract} copy() : None
        + {abstract} get_headers() : List[str]
    }
    abstract class APlayer {
        + handle_config_overrides(default_config, overrides) : GameConfig
        + play(config) : None
        + {abstract} make_decision(state: AGameState) 
        + write_stats(state: AGameState) : None
        + quit() : None
        + on_quit() : None
        + on_game_over(state: AGameState) : None
        + on_decision_made(state: AGameState, player_move) : None
        + on_move_made(old_state : AGameState, new_state : AGameState, player_move) : None
    }

    APlayer --> AGameCore
    APlayer --> AGameState
    AGameCore -> AGameState
    

============================
Diagram sekwencji dla gracza
============================

.. uml::
    participant start


    create participant Player
    start -> Player
    create participant GameCore
    Player -> GameCore
    start -> Player: play(GameConfig config)

    
    activate Player
    

    loop Ta pętla będzie wykonywana dopóki użytkownik nie zakończy gry
        Player -> GameCore: restart(GameConfig config)
        activate GameCore
        return GameState

        loop Ta pętla będzie wykonywana tak długo jak gracz nie przegra albo nie zakończy gry
            Player -> Player: make_decision(GameState state) : tuple[PlayerMove move, bool is_running] 

            Player -> GameCore: make_move(PlayerMove move)

            activate GameCore
            return GameState
        end

        
    end
    Player -> GameCore: quit()
    activate GameCore
    return 

    destroy GameCore
    return Najlepszy wynik : int



============
Gry
============

Ten dokument opisywał ogólną strukturę kodu źródłowego dla gier. Poniżej znajdują się linki do dokumentacji dla poszczególnych gier:

.. toctree::
    :maxdepth: 2

    snake/index.rst

