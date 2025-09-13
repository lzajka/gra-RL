from gymnasium import Env
import vizdoom as vd
from .game_config import GameConfig
from .action import Action

class VizDoomEnv(Env):
    def __init__(self, config : GameConfig):
        self.config = config
        
        self.game = vd.DoomGame()
        self.game.load_config(config.scenario)
        self.game.init()

    def step(self, action : Action):
        vaction = action.to_vector()
        
        old_state = self.game.get_state()

        reward = self.game.make_action(vaction, 4)

        new_state = self.game.get_state()

        done = self.game.is_episode_finished()

        return old_state, reward, new_state, done

    def reset(self):
        self.game.new_episode()
        return self.game.get_state()


    def close(self):
        self.game.close()