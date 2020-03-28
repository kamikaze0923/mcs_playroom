"""
Base class implementation for ai2thor environments wrapper, which adds an openAI gym interface for
inheriting the predefined methods and can be extended for particular tasks.
"""

import os
import gym

from gym.utils import seeding

import machine_common_sense


class McsEnv(gym.Env):
    """
    Wrapper base class
    """
    def __init__(self, seed=None):
        self.np_random = None
        if seed:
            self.seed(seed)

        self.controller = machine_common_sense.MCS_Controller_AI2THOR(
            os.path.join(os.getcwd(), "gym_ai2thor/unity_app/MCS-AI2-THOR-Unity-App-v0.0.2.x86_64")
        )

        self.scene_config, status = machine_common_sense.MCS.load_config_json_file(
            os.path.join(os.getcwd(), "gym_ai2thor/scenes/playroom.json")
        )

        self.all_actions_str = self.controller.ACTION_LIST.copy()
        self.task = None

    def step(self, action):
        return NotImplementedError

    def get_observation(self):
        return NotImplementedError

    def reset(self):
        # print('Resetting environment and starting new episode')
        self.step_output = self.controller.start_scene(self.scene_config)
        self.task.reset()
        return self.get_observation()

    def seed(self, seed=None):
        self.np_random, seed1 = seeding.np_random(seed)
        # Derive a random seed. This gets passed as a uint, but gets
        # checked as an int elsewhere, so we need to keep it below
        # 2**31.
        return seed1

    def close(self):
        self.controller.end_scene(None, None)


if __name__ == '__main__':
    McsEnv()
