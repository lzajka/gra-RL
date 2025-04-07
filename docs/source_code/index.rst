Kod źródłowy
=========================
Katalog `src` jest podzielony na moduły, które zawierają kod źródłowy dla poszczególnych gier. W celu ujednolicenia struktury kodu, każdy moduł zawiera następujące pliki:



- `src/general/igame_core.py` - plik zawierający interfejs `IGameCore`. Jest on odpowiedzialny za logikę gry, oraz obsługę `pygame`. Przechwytuje wydarzenia, a następnie razem z stanem `AGameState` przekazuje je do
- `src/general/aplayer.py` - plik zawierający klasę abstrakcyjną `APlayer`. Jest ona odpowiedzialna za obsługę gracza, zarówno człowieka jak i agenta AI. Decyzje podejmowane są na podstawie przesłanego przez klasę implementującą `IGameCore` stanu gry opartego na `AGameState`.
- `src/general/agame_state.py` - plik zawierający klasę abstrakcyjną `AGameState`. Jest ona odpowiedzialna za przechowywanie informacji na temat stanu gry, takich jak wynik, czy gra jest zakończona, oraz przechwyconych wydarzeń `pygame.event`.
- `src/<gra>/human_player.py` - plik zawierający klasę `Player` implementującą `APlayer`. Jest odpowiedzialna za obsługę gry przez człowieka.
- `src/<gra>/agents/<nazwa_agenta>.py` - plik zawierający klasę `Player` implementującą `APlayer`, Jest odpowiedzialna za obsługę gry przez agenta RL.
- `src/<gra>/game_config.py` - plik zawierający konfigurację gry, jest on odpowiedzialny za ogólną konfiguracje. Konfiguracja podana przez agenta.
- `src/<gra>/player_move.py` - plik zawierający klasę `PlayerMove`, która jest odpowiedzialna za przechowywanie wybranej przez gracza akcji.


============
Diagram klas
============



.. uml::

    abstract class AGameState {
        + score : int
        + is_game_over : bool
        + events : List[pygame.event]
    }

    interface IGameCore {
    + {abstract} make_move(PlayerMove move) : AGameState
    + {abstract} restart(GameConfig config) : AGameState
    + {abstract} quit()
    }

    abstract APlayer {
    + play(GameConfig config) : int
    # {abstract} make_decision(AGameState state) : tuple[PlayerMove move, bool is_running] 
    }

    class HumanPlayer implements APlayer {
    + play(GameConfig config) : int
    }

    class AgentPlayer implements APlayer {
    + play(GameConfig config) : int
    }    

    APlayer *-- IGameCore
    AGameState --* IGameCore

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

