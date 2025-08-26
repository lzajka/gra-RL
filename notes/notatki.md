# 14-08

## Ilość poziomów

- Byłem niepewny czy zaimplementować większą ilość poziomów ponieważ konieczne być może trenowanie pacmana na każdym poziomie.
- Zdecydowałem że mogę dodać. Będę trenował na niższym poziomie dopóki pacman nie stanie się wystarczająco dobry, wtedy dam wyższy poziom. Porównam wyniki uzyskane na każdym poziomie przez człowieka i AI.

## Cornering
- Zdecydowałem że go nie zaimplementuje. Implementacja wymagała by dużych zmian związanych z poruszaniem się aktorów. Dodałoby to również dodatkowe decyzje. 
- **Decyzja**: Osiągne podobny efekt zwiększając prędkość razy 2 kiedy następuje zmiana kierunku.

## Zmiana kierunku pacmana
- Okazuje się, że pacman może zmieniać kierunek nawet wtedy, gdy nie dotyka ściany.
- Implementacja tego dodałaby wiele możliwych sytuacji, w których AI mogłoby decydować.
- Coś takiego pozwala na "stanie w miejcu przez pacmana", które może się w niektórych sytuacjach przydać.
- Nawet implementacja postoju dodałaby 60 sytuacji/s w których Pacman decyduje.
- Czasami dobrym pomysłem może być zachowanie odpowiedniego dystansu między poruszającymi się duchami, więc danie częściowej zamiast całkowitej kontroli pogorszyłoby efektywność AI.
- Czy AI będzie mogło efektywnie decydować jaka liczba zmiennoprzecinkowa byłaby ok?
- Czasami może dobry byłby wczesny powrót.
- **Decyzja**: Ani gracz ani AI nie będzie mogło dowolnie zmieniać kierunku. Ewentualnie zmniejsze trudność poziomów.

# 15-08
## Fright - RNG
- AI nie będzie w stanie efektywnie przewidywać zachowania duchów w trybie FRIGHT
- Może generowanie liczby na podstawie ducha + obecnego pola zadziałałoby
- Próbowałem sterować wybieraniem kierunku na podstawie wybierania losowego pola jako celu, coś takiego powodowałoby, że w wypadku braku dostępności wszystkich kierunków, niektóre byłyby preferowane.
- Ostatecznie sprawdzam wszystkie sąsiednie pola, wybieram dostępne, a następnie losuje
# 15-09
- Powrót do spawnu nie działa na obecnej mapie
  - Użyje mapy oryginalnej
## Duch może utknąć w miejscu podczas powrotu
- Duch podczas powrotu do Spawna utykał, próbowałem ten problem zdebugować za pomocą pysnooper
  - Dane tekstowe nie były zbyt przyjazne
- Ponieważ zachowanie duchów jest deterministyczne, wykonanie tych samych ruchów da oczekiwany rezultat
  - Wykorzystałem debugger vscode  
- Problem był z sposobem w jaki był wybierany następny kierunek.
# 21-08
- Próbowałem dodać informację o ilości punktów na każdą ścieżkę, jednak zorientowałem się, że w moim przypadku wystarczy informacja o odwiedzeniu ścieżki, co wymaga takiej samej ilości neuronów w warstwie wejścia
# 22-08
## Kopiowanie danych
- Konieczne było poprawienie kopiowania obecnego stanu
- Kopiowanie składa się z wykonania kopii zmiennych stanu, w tym labiryntu
- Kopiowanie całego labiryntu składa się z:
  - Obiekty statyczna - czyli te których stan pozostaje zawsze taki sam zwracają jedynie obecną instancję. W tym przypadku warto pamiętać o tym, że nie można w jakikolwiek sposób zmieniać ich stanu. Jest to domyślny sposób "kopiowania". Następnie te są manualnie przypisywane do odpowiedniej pozycji w nowej instancji labiryntu
  - Obiekty dynamiczne - Czyli te których stan się zmienia, do tych należą aktorzy oraz punkty nadpisują domyślną metodę kopiowania
- Ponieważ w przypadku gracza decyzja może być podjęta nawet jak pacman stoi w miejscu to wtedy konieczne byłoby wykonanie 60 kopii na sekundę, co jest kosztowne. 
### Kopiowanie danych duchów
- Ponieważ aktorzy są obiektem w labiryncie, ich kopia jest wykonywana w czasie wykonywania kopii labiryntu.
- Jako argumenty przekazywane są labirynt oraz stan. 
## Kiedy są podejmowane decyzję.
W celu ograniczenia ilości podejmowanych decyzji, a za tym ograniczeniem ilości wykonanych kopii, dodałem nową metodę która mówi czy w danym przypadku można ją podjąć. Jeżeli nie:
  - Ostatni stan nie jest aktualizowany.
  - Kopia nie jest wykonywana.
  - Numer ruchu nie jest aktualizowany.
  - Decyzja nie jest podejmowana.
  - `on_move_made` nie jest wywoływany
  - Statystyki nie są zapisywane
  - `GameCore.make_move()` otrzymuje informację, że decyzja to `None`
- W przypadku AI pacmana decyzje są podejmowane:
  - W wypadku w którym pacman w następnej ramce zmieni pozycję
  - co 1s jeżeli stoi
  - Po przejściu do stanu końcowego (przegrana/wygrana)
