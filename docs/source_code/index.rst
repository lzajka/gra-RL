Kod źródłowy
=========================
Katalog `src` jest podzielony na moduły, które zawierają kod źródłowy dla poszczególnych gier. W celu ujednolicenia struktury kodu, każdy moduł zawiera następujące pliki:



- `game_core.py` - plik zawierający klasę `GameCore`, która jest odpowiedzialna za logikę gry. Udostępnia ona metody do przeprowadzania ruchów, sprawdzania stanu gry, itp.
- `player.py` - plik zawiera interfejs `Player`. Celem klas implementujących ten interfejs jest gra w grę.
- `human_player.py` - plik zawierający klasę `HumanPlayer`, która jest odpowiedzialna za obsługę gry przez człowieka. Implementuję interfejs `Player`.
- `agent_player.py` - plik zawierający klasę `AgentPlayer`, która jest odpowiedzialna za obsługę gry przez agenta RL. Implementuję interfejs `Player`.
- `game_config.py` - plik zawierający konfigurację gry, jest on odpowiedzialny za ogólną konfiguracje. Konfiguracja podana przez agenta 


============
Diagram klas
============



.. uml::

    class GameCore {
    + make_move(PlayerMove move)
    + restart(GameConfig config)
    + quit()
    }

    interface Player {
    + notify(GameState state)
    + play(GameConfig config)
    }

    class HumanPlayer implements Player {
    + notify(GameState state)
    + play(GameConfig config)
    }

    class AgentPlayer implements Player {
    + notify(GameState state)
    + play(GameConfig config)
    }    


Klasa `Player` jest interfejsem, i odnosi się ona do podejmującego decyzje gracza. Klasa `HumanPlayer` implementuje ten interfejs i jest odpowiedzialna za obsługę gry przez człowieka. Klasa `AgentPlayer` również implementuje ten interfejs i jest odpowiedzialna za obsługę gry przez agenta RL. 

Klasa `GameCore` jest odpowiedzialna za logikę i wyświetlanie gry. Udostępnia ona metody do przeprowadzania ruchów, sprawdzania stanu gry, itp.

============
Gry
============

Ten dokument opisywał ogólną strukturę kodu źródłowego dla gier. Poniżej znajdują się linki do dokumentacji dla poszczególnych gier:

.. toctree::
    :maxdepth: 2

    snake/index.rst

