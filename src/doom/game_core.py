from src.general.agame_core import AGameCore
import vizdoom as vd
import os
from .game_config import GameConfig
from .game_state import GameState
from .action import Action


class GameCore(AGameCore):
    main_instance = None

    def __init__(self):
        if GameCore.main_instance is not None:
            raise Exception('Nie można utworzyć więcej niż jednej instancji GameCore')
        
        super().__init__()
        self.vd = vd.DoomGame()


        self.episode_number = 0
        GameCore.main_instance = self
        self.cfg : GameConfig = None

    def get_default_config(self):
        return GameConfig()

    def on_restart(self, config : GameConfig):
        if self.episode_number == 0:
            self.vd.load_config(os.path.join(vd.scenarios_path, config.SCENARIO))
            if config.ARGS is not None: self.vd.set_game_args(config.ARGS)
            if config.MODE is not None: self.vd.set_mode(config.MODE)
            if config.RES is not None: self.vd.set_screen_resolution(config.RES)
            self.vd.init()
        self.vd.new_episode()
        self.cfg = self.get_default_config()
        self.episode_number += 1
        return self.state

    @property
    def state(self):
        return GameState(self.vd.get_state())

    def on_make_move(self, move : Action):
        #self.clock.tick(self.cfg.FPS)
        if move is not None:
            self.vd.make_action(move.to_vector())
        else:
            self.vd.advance_action()
        return self.state    
    def quit(self):
        self.vd.close()

    @property
    def is_game_over(self):
        return self.vd.is_episode_finished()