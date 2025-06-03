Architektura
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
        + APlayer(self, game, args, config_overrides)
        + {abstract} APlayer(args, overrides) : None
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

    class GameCore extends AGameCore {
        + quit() : None
        + on_make_move(move) : None
        + on_restart(config) : None
        + get_default_config() : GameConfig
    }
    class GameState extends AGameState {
        + to_list() : List[str]
        + copy() : None
        + get_headers() : List[str]
    }
    class Player extends APlayer {
        + APlayer(args, overrides) : None
        + make_decision(state: AGameState) 
    }

    APlayer --> AGameCore
    APlayer --> AGameState
    AGameCore -> AGameState
    

============================
Diagram sekwencji gry
============================

.. uml::

    participant start

    create Player
    activate start
    start -> Player : Player(args, overrides)
    activate Player
    Player -> Player : Player(self, game, args, config_overrides)
    activate Player
    create GameCore
    Player -> GameCore : GameCore(args, overrides)
    activate GameCore
    return
    return
    Player -> GameCore : get_default_config()
    activate GameCore
    return
    Player -> Player: handle_config_overrides(default_config, overrides)
    activate Player
    return
    return
    start -> Player : play(config)
    activate Player
    loop while is_running
        Player -> GameCore : restart(config)
        activate GameCore
        GameCore -> GameCore : on_restart(config)
        activate GameCore
        return
        return AGameState
        Player -> Player : write_stats(state: AGameState)
        activate Player
        return 
        loop while not state.is_game_over and is_running
            Player -> Player : make_decision(state: AGameState)
            activate Player
            return [player_move, is_running]
            Player -> Player : on_decision_made(state: AGameState, player_move)
            activate Player
            return
            opt !is_running
                break 
                end
            end
            
            Player -> GameCore : make_move(player_move)
            activate GameCore
            GameCore -> GameCore : on_make_move(move)
            activate GameCore
            return
            return AGameState
            Player -> Player : on_move_made(old_state : AGameState, new_state : AGameState, player_move)
            activate Player
            return
            Player -> Player : write_stats(state: AGameState)
            activate Player
            return
            end
        Player -> Player : on_game_over(state: AGameState)
        activate Player
        return
    end
    Player -> Player : quit()
    activate Player
    Player -> Player : on_quit()
    activate Player
    return
    Player -> GameCore : quit()
    activate GameCore
    return
    return
    return


============
Gry
============

Ten dokument opisywał ogólną strukturę kodu źródłowego dla gier. Poniżej znajdują się linki do dokumentacji dla poszczególnych gier:

.. toctree::
    :maxdepth: 2

    snake/index.rst
    pacman/index.rst
