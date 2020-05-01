
from gym.spaces import Discrete
from point_goal_navigation.navigator import NavigatorResNet

from gym_ai2thor.envs.mcs_wrapper import McsWrapper
import machine_common_sense
import numpy as np


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
            # raise AttributeError('Navigator Should End Before Stop')
        if epsd_collector is not None:
            epsd_collector.add_experience(self.step_output, action_str)

        return self.step_output

    def micro_move(self, env, goal):
        current_x, current_z = env.step_output.position['x'], env.step_output.position['z']
        goal_x, _, goal_z = goal
        delta_x, delta_z = goal_x - current_x, goal_z - current_z
        amount = (delta_x ** 2 + delta_z ** 2) ** 0.5
        rotate = NavigatorResNet.get_polar_direction(goal, env.step_output) * 360 / (2 * np.pi)
        super().step(action='RotateLook', rotation=-rotate)
        while amount > machine_common_sense.mcs_controller_ai2thor.MAX_MOVE_DISTANCE:
            super().step(action='MoveAhead', amount=1)
            amount -= machine_common_sense.mcs_controller_ai2thor.MAX_MOVE_DISTANCE
        super().step(action='MoveAhead', amount=amount / machine_common_sense.mcs_controller_ai2thor.MAX_MOVE_DISTANCE)

        # current_x, current_z = env.step_output.position['x'], env.step_output.position['z']
        # delta_x, delta_z = goal_x - current_x, goal_z - current_z
        # amount = (delta_x ** 2 + delta_z ** 2) ** 0.5
        # print(amount)
        # print(rotate)









