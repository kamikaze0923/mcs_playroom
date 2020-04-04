"""
Base class implementation for ai2thor environments wrapper, which adds an openAI gym interface for
inheriting the predefined methods and can be extended for particular tasks.
"""

import os
import gym

from gym.utils import seeding
import random

import machine_common_sense
import gym_ai2thor
from gym_ai2thor.utils import read_config



class McsEnv(gym.Env):
    """
    Wrapper base class
    """
    POSSIBLE_INIT_ROTATION = [i*10 for i in range(360)]
    POSSIBLE_INIT_X = [-2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5]
    POSSIBLE_INIT_Z = [-2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5]

    def __init__(self, config_file, config_dict, seed=None):
        self.np_random = None
        if seed:
            self.seed(seed)

        self.config = read_config(config_file, config_dict)

        self.rgb_sensor = True if self.config['rgb_sensor'] else False
        self.depth_sensor = True if self.config['depth_sensor'] else False

        self.controller = machine_common_sense.MCS_Controller_AI2THOR(
            os.path.join(os.getcwd(), "gym_ai2thor/unity_app/MCS-AI2-THOR-Unity-App-v0.0.2.x86_64"),
            renderDepthImage=self.depth_sensor, renderObjectImage=False
        )

        self.scene_config, status = machine_common_sense.MCS.load_config_json_file(
            os.path.join(os.getcwd(), "gym_ai2thor/scenes/playroom.json")
        )


    def step(self, action):
        return NotImplementedError

    def get_observation(self):
        return NotImplementedError

    def reset(self):
        return NotImplementedError

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
