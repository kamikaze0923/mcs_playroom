"""
Base class implementation for ai2thor environments wrapper, which adds an openAI gym interface for
inheriting the predefined methods and can be extended for particular tasks.
"""

import os
import gym
import platform

from gym.utils import seeding
from gym.spaces import Box
import numpy as np
from skimage import transform
import random

import machine_common_sense
from gym_ai2thor.utils import read_config

class ObeserationSpace:
    def __init__(self):
        self.spaces = None

class McsEnv(gym.Env):
    """
    Wrapper base class
    """
    POSSIBLE_INIT_ROTATION = [i*10 for i in range(360)]
    POSSIBLE_INIT_X = [-4, -3, 3, 4]
    POSSIBLE_INIT_Z = [-4, -3, 3, 4]

    def __init__(self, config_file="config_files/config_base.json", config_dict=None, seed=None):
        self.np_random = None
        if seed:
            self.seed(seed)

        self.config = read_config(config_file, config_dict)

        self.rgb_sensor = True if self.config['rgb_sensor'] else False
        self.depth_sensor = True if self.config['depth_sensor'] else False

        self.observation_spaces = ObeserationSpace()
        self.observation_spaces.spaces = {
            'pointgoal_with_gps_compass': Box(
                low=np.finfo(np.float32).min, high=np.finfo(np.float32).max,
                dtype=np.float32, shape=(2,)
            )
        }
        if self.rgb_sensor:
            self.observation_spaces.spaces['rgb'] = Box(low=0, high=255, dtype = np.uint8,
                                                shape=(self.config['resolution'][0], self.config['resolution'][1], 3))
        if self.depth_sensor:
            self.observation_spaces.spaces['depth'] = Box(low=0, high=255, dtype=np.uint8,
                                                  shape=(self.config['resolution'][0], self.config['resolution'][1], 1))

        if platform.system() == "Linux":
            app = "gym_ai2thor/unity_app/MCS-AI2-THOR-Unity-App-v0.0.2.x86_64"
        elif platform.system() == "Darwin":
            app = "gym_ai2thor/unity_app/MCSai2thor.app/Contents/MacOS/MCSai2thor"
        else:
            app = None

        self.controller = machine_common_sense.MCS_Controller_AI2THOR(
            os.path.join(os.getcwd(), app),
            # renderDepthImage=self.depth_sensor, renderObjectImage=True
        )

        self.scene_config, status = machine_common_sense.MCS.load_config_json_file(
            os.path.join(os.getcwd(), "gym_ai2thor/scenes/playroom.json")
        )

        self.step_output = None

        self.rotation_state = None # same as MCS internal
        self.abs_rotation = 10 # same as settings in habitat, right is positive

    def step(self, action):
        return NotImplementedError

    def reset(self):
        # self.rotation_state = random.sample(self.POSSIBLE_INIT_ROTATION, 1)[0]
        # init_x = random.sample(self.POSSIBLE_INIT_X, 1)[0]
        # init_z = random.sample(self.POSSIBLE_INIT_Z, 1)[0]
        # self.scene_config["performerStart"] = {
        #     "position": {
        #         "x": init_x,
        #         "z": init_z
        #     },
        #     "rotation": {
        #         "y": self.rotation_state
        #     }
        # }
        self.rotation_state = 20
        init_x = 4
        init_z = 4
        self.scene_config["performerStart"] = {
            "position": {
                "x": init_x,
                "z": init_z
            },
            "rotation": {
                "y": self.rotation_state
            }
        }
        self.step_output = self.controller.start_scene(self.scene_config)


    def get_rgb(self):
        img = self.step_output.image_list[0].convert(mode="P").convert("RGB")
        img = np.array(img).transpose(2, 0, 1)
        return img

    def get_depth_rgb(self):
        img1 = self.get_rgb()
        assert self.depth_sensor
        img2 = self.step_output.depth_mask_list[0].convert(mode="L").convert("RGB")
        img2 = np.array(img2).transpose(2, 0, 1)
        img = np.concatenate([img1, img2], axis=2)
        return img

    def preprocess(self, img):
        img = np.array(img)
        if len(img.shape) == 2:
            img = np.expand_dims(img, axis=-1)
        img = transform.resize(img, self.config['resolution'], mode='reflect')
        img = img.astype(np.float32)
        return img

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
