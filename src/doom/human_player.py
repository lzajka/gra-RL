from src.general.aplayer import APlayer
import pygame
from .game_core import GameCore
from .action import Action
class Player(APlayer):
    def getGame(self) -> GameCore:
        r = GameCore.main_instance
        if r is None:
            r = GameCore()
        return r
      
    def make_decision(self, state):
        
        return self.event_handling()

    def event_handling(self):
        events = pygame.event.get()
        controls = {
            pygame.K_a : Action.MOVE_LEFT,
            pygame.K_d : Action.MOVE_RIGHT,
            pygame.K_SPACE : Action.SHOOT           # Ponieważ jestem na laptopie niech będzie spacja
        }
        action = None
        for event in events:
            is_keydown = pygame.KEYDOWN == event.type
            if is_keydown and event.key in controls.keys():
                action = controls[event.key]
            elif (is_keydown and event.key == pygame.K_Q) or event.type == pygame.QUIT:
                return [None, False]

        return [action, True]