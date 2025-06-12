Pacman
======

.. note::
    Ta strona zawiera dokumentację dotyczącą architektury gry pacman. Informacje na temat zasad gry, w tym zachowania duchów, znajdują się w `osobnym dokumencie <rules.rst>`_.

=========
Definicje
=========
- **Aktor** - byt, który może wykonywać akcje w grze. Do aktorów zaliczają się graczy i duchy. 
   - **Gracz** - byt kontrolowany przez użytkownika. Użytkownikiem może być człowiek lub sztuczna inteligencja.
- **Ruch** - akcja wykonywana przez gracza lub ducha, która zmienia stan gry.
- **Konfiguracja gry** - zestaw parametrów definiujących zasady i ustawienia gry, takie jak liczba duchów, prędkość graczy itp.
- **Stan gry** - reprezentacja aktualnego stanu gry, zawierająca informacje o położeniu graczy, duchów, punktów itp. 
- **Silnik gry** - Główny komponent odpowiedzialny za zarządzanie logiką gry, w tym aktualizację stanu gry, obsługę ruchów graczy i duchów oraz sprawdzanie warunków zwycięstwa i przegranej.
- **Plansza**  - dwuwymiarowa siatka, na której rozgrywa się gra. Zawiera informacje o ścianach, punktach i innych elementach.
   - **Punkt** - element planszy, który gracz może zebrać, aby zdobyć punkty. Punkty mogą być zwykłe lub specjalne (np. super punkty).
      - **Super punkt**  - specjalny punkt, który daje graczowi przewagę nad duchami, umożliwiając mu ich zjedzenie.
   - **Ściana** - element planszy, który blokuje ruch graczy i duchów.
   - **Teleport** - specjalny element planszy, który umożliwia graczom i duchom teleportację z jednego miejsca na drugie.
   - **Spawn duchów** - miejsce na planszy, gdzie duchy pojawiają się na początku gry lub po zjedzeniu.
   - **Spawn gracza** - miejsce na planszy, gdzie gracz pojawia się na początku gry, lub po utracie życia.
- **Kolizja** - sytuacja, w której dwa obiekty znajdują się w tej samej komórce na planszy.
- **Zjedzenie** - akcja, która ma miejsce, gdy gracz zbiera punkt,super punkt, lub gdy gracz zjada ducha. Aby do niej doszło, musi zajść kolizja między graczem a punktem, super punktem lub duchem.
- **Pole widzenia** - obszar wokół ducha, w którym może on wykryć gracza.
- **Wymagania spawnu** - warunki, które muszą być spełnione, aby duch mógł się pojawić na planszy.
- **Aktywność powerup** - Stan w którym gracz ma aktywny super punkt, co pozwala mu na zjedzenie duchów.

============================
Ogólna idea działania modeli
============================

============
Diagram klas
============

.. plantuml:: class_diagram.puml
   :alt: Diagram klas gry Pacman


.. toctree::
   :maxdepth: 2
   :caption: Spis treści

   ghost_behavior
   rules
   sequence_diagrams/index

