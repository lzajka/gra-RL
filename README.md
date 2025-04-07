# gra-RL
Projekty indywidualny - Implementacja gry wykorzystującej uczenie ze wzmocnieniem.

> [!NOTE]
> Gałąź `master` wykorzystuję jako stabilną gałąź. Najnowsze zmiany znajdują się na gałęzi `dev`.

# Zakres pracy:
- [x] Zapoznanie się z tematyką RL (Snake)
- Implementacja
  - [x]   własnej gry
  - [x]   oraz RL
- [ ] Porównanie wyników człowieka z zaimplementowanym algorytmem
- [ ] Raport końcowy

# Struktura projektu

- `src` - Katalog zawierający kody źródłowe gier, które wykorzystuję uczenie przez wzmocnienie. Katalogi zawarte w tym katalogu odnoszą się do poszczególnych gier.
- `docs` - Katalog zawierający dalszą dokumentację i raporty.

# Dostępne gry
- [ ] snake

# Uruchamianie

Aby uruchomić projekt, konieczne jest posiadanie zainstalowanego Pythona. Zalecana wersja to Python 3.13.2 lub nowsza.

Następnie należy upewnić się, czy zależności określone w pliku `requirements.txt` są zainstalowane. 

> [!NOTE] Środowiska wirtualne
> Zalecana jest instalacja pakietów pythonowych w [środowisku wirtualnym](https://docs.python.org/3/library/venv.html).

Jeżeli wszystkie zależności są spełnione, to można uruchamiać projekty za pomocą narzędzia `start.py` znajdującego się w katalogu nadrzędnym. Informacje o składni można uzyskać wyświetlając menu pomocy: `python start.py --help` (Windows) lub `./start.py --help` (Linux)