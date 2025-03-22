#!/usr/bin/env python3
import sys
import argparse
import importlib
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser(
    description='Skrypt służący do uruchamiania gier. Pozwala na tryb gry z agentem, lub bez.',
    epilog='Projekt wykonany przez Łukasza Czajkę, w ramach projektu indywidualnego "Implementacja gry wykorzystującej uczenie ze wzmocnieniem." na Politechnice Warszawskiej w roku akademickim 2024/2025.'
    )

parser.add_argument('game', type=str, help='Nazwa gry do uruchomienia.')
parser.add_argument('-l', '--list', action='store_true', help='Wyświetla listę dostępnych gier.')
parser.add_argument('-a', '--agent', type=str, help='Nazwa agenta do uruchomienia. Jeżeli argumentu nie podano, gra zostanie uruchomiona w trybie dla człowieka. Jeżeli argument podano bez wartości, zostanie uruchomiony domślny agent "default".', nargs='?', const='default', default=None)

args = parser.parse_args()
game_name = args.game
agent_name = args.agent
is_agent_mode_enabled = agent_name is not None

game_submodule_path = f'agents.{agent_name}' if is_agent_mode_enabled else 'game'
full_game_module_path = f'src.{game_name}.{game_submodule_path}'

logger.debug(f'Importuje: {full_game_module_path}')
game_module = importlib.import_module(full_game_module_path)
