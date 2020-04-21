
from gym.spaces import Discrete
import numpy as np

from gym_ai2thor.envs.mcs_wrapper import McsWrapper


class McsNavWrapper(McsWrapper):

    def __init__(self, env):
        super().__init__(env)
        self.action_names = ["Stop", "MoveAhead", "RotateLeft", "RotateRight"]# order matters
        self.action_space = Discrete(len(self.action_names))

    def step(self, action, epsd_collector=None):
        action_str = self.action_names[action]
        if action_str.startswith('Rotate'):
            rotation = -self.ABS_ROTATION if action_str == 'RotateLeft' else self.ABS_ROTATION
            super().step(action='RotateLook', rotation=rotation)
        elif action_str == 'MoveAhead':
            super().step(action=action_str, amount=0.5)
        else:
            assert action_str == 'Stop'
            raise AttributeError('Navigator Should End Before Stop')
        if epsd_collector is not None:
            epsd_collector.add_experience(self.step_output, action_str)

        return self.step_output







