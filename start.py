#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
import sys
import argparse, argcomplete
from argcomplete.completers import FilesCompleter, DirectoriesCompleter
import importlib
import logging
import os

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Definicja argumentów

parser = argparse.ArgumentParser(
    description='Skrypt służący do uruchamiania gier. Pozwala na tryb gry z agentem, lub bez.',
    epilog='Projekt wykonany przez Łukasza Czajkę, w ramach projektu indywidualnego "Implementacja gry wykorzystującej uczenie ze wzmocnieniem." na Politechnice Warszawskiej w roku akademickim 2024/2025.'
    )
subparsers = parser.add_subparsers(dest='command', required=True, title='Dostępne komendy')

launch_parser = subparsers.add_parser('launch', help='Uruchamia grę.')
launch_parser.add_argument('game', type=str, help='Nazwa gry do uruchomienia.')

agent_mode_group = launch_parser.add_argument_group('Argumenty związane z agentem')
agent_mode_group.add_argument('-a', '--agent', type=str, 
                       help='Nazwa agenta do uruchomienia. Jeżeli argumentu nie podano, gra zostanie uruchomiona w trybie dla człowieka. Jeżeli argument podano bez wartości, zostanie uruchomiony domyślny agent "default".', 
                       nargs='?', const='default', default=None)

model_group = agent_mode_group.add_mutually_exclusive_group(required=False)

model_group.add_argument('-l', '--load-model', type=str, dest='load_model', 
                              help='Ścieżka do pliku z modelem agenta, którego chcemy wczytać.', default=None)
model_group.add_argument('-s', '--save-model', type=str, dest='save_model',
                              help='Ścieżka do pliku, w którym chcemy zapisać model agenta.', default=None)

launch_parser.add_argument('-o', '--output-stats', type=str, 
                       help='Ścieżka do pliku, w którym będą zapisywane statystyki gry. Jeżeli argumentu nie podano, statystyki nie będą zapisywane.', 
                       default=None).completer = FilesCompleter(directories=False)

launch_parser.add_argument('--log-level', type=str,
                       help='Poziom logowania. Możliwe wartości: DEBUG, INFO, WARNING, ERROR, CRITICAL. Domyślnie DEBUG.', 
                       default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])

launch_parser.add_argument('-c', '--config', type=str, nargs='+', metavar='KLUCZ=WARTOŚĆ',
                           help='Pozwala na tymczasowe nadpisanie określonej zmiennej w konfiguracji.',
                           required=False, default=[])

subparsers.add_parser('list', help='Wyświetla listę dostępnych gier.')
argcomplete.autocomplete(parser)
args = parser.parse_args()


def map_str_to_log_level(log_level_str):
    """Mapuje string do poziomu logowania.

    Args:
        log_level_str (str): String do zmapowania.

    Returns:
        int: Poziom logowania.
    """
    levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    return levels.get(log_level_str, logging.DEBUG)

def parse_key_value_pairs(pairs):
    """Funkcja parsuje pary klucz-wartość z listy.

    Args:
        pairs (list): Lista par klucz-wartość w formacie tekstowym.

    Returns:
        dict: Słownik z parametrami.
    """
    params = {}
    for pair in pairs:
        key, value = pair.split('=')
        params[key] = value
    return params

# Definicje funkcji podprogramów

def play():
    
    game_name = args.game
    agent_name = args.agent

    is_agent_mode_enabled = agent_name is not None

    logging.basicConfig(level=map_str_to_log_level(args.log_level))
    overrides = parse_key_value_pairs(args.config)


    if game_name == 'general':
        logger.error('Nazwa gry nie może być "general".')
        sys.exit(1)

    game_submodule_path = f'agents.{agent_name}.player' if is_agent_mode_enabled else 'human_player'
    full_game_module_path = f'src.{game_name}.{game_submodule_path}'

    logger.debug(f'Importuje: {full_game_module_path}')
    game_module = importlib.import_module(full_game_module_path)

    
    player = game_module.Player(args, overrides)
    player.play()

def list():
    print('Dostępne gry:')
    dirs = os.listdir('src')
    dirs.remove('general')
    print('\n'.join(dirs))
    exit(0)

# Część odpowiedzialna za uruchomienie podprogramu w zależności od args.command

if args.command == 'launch':
    play()
elif args.command == 'list':
    list()
else:
    print('Nieznana komenda. Użyj --help aby zobaczyć dostępne komendy.')
    sys.exit(1)