from src.general.aplayer import APlayer
import pygame
from .game_core import GameCore
from .action import Action
import vizdoom as vd
from . import overrides

class Player(APlayer):
    def getGame(self) -> GameCore:
        r = GameCore.main_instance
        if r is None:
            r = GameCore()
        return r

    def make_decision(self, state):
        
        g = self.getGame()

        return [None, g.vd.is_running()]
