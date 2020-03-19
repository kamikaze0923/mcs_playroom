"""
Base class implementation for ai2thor environments wrapper, which adds an openAI gym interface for
inheriting the predefined methods and can be extended for particular tasks.
"""

import os

import ai2thor.controller
import numpy as np
from skimage import transform
from collections import defaultdict

import gym
from gym import error, spaces
from gym.utils import seeding
from gym_ai2thor.image_processing import rgb2gray
from gym_ai2thor.utils import read_config
import gym_ai2thor.tasks
import machine_common_sense

import torch
from PIL import Image


class McsEnv(gym.Env):
    """
    Wrapper base class
    """
    def __init__(self, seed=None, config_file='config_files/config_example3.json', config_dict=None):
        """
        :param seed:         (int)   Random seed
        :param config_file:  (str)   Path to environment configuration file. Either absolute or
                                     relative path to the root of this repository.
        :param: config_dict: (dict)  Overrides specific fields from the input configuration file.
        """
        # Loads config settings from file
        self.config = read_config(config_file, config_dict)
        self.scene_id = self.config['scene_id']
        # Randomness settings
        self.np_random = None
        if seed:
            self.seed(seed)

        self.controller = machine_common_sense.MCS_Controller_AI2THOR(
            os.path.join(os.getcwd(), "gym_ai2thor/unity_app/MCS-AI2-THOR-Unity-App-v0.0.1.x86_64")
        )

        self.scene_config, status = machine_common_sense.MCS.load_config_json_file(
            os.path.join(os.getcwd(), "gym_ai2thor/scenes/playroom.json")
        )

        all_actions_str = self.controller.ACTION_LIST.copy()
        if not self.config['open_close_interaction']:
            all_actions_str.remove('OpenObject')
            all_actions_str.remove('CloseObject')
        if not self.config['pickup_put_interaction']:
            all_actions_str.remove('PickupObject')
            all_actions_str.remove('PutObject')
        if not self.config['push_pull_interation']:
            all_actions_str.remove('PushObject')
            all_actions_str.remove('PullObject')
        if not self.config['throw_interation']:
            all_actions_str.remove('ThrowObject')
        if not self.config['drop_interation']:
            all_actions_str.remove('DropObject')
        if 'RotateLook' in all_actions_str:
            all_actions_str.remove('RotateLook')
            all_actions_str.append('RotateRight')
            all_actions_str.append('RotateLeft')
            all_actions_str.append('LookUp')
            all_actions_str.append('LookDown')

        self.action_names = all_actions_str
        self.action_space = spaces.Discrete(len(self.action_names))
        self.channels = 1 if self.config['grayscale'] else 3
        self.observation_space = spaces.Box(low=0, high=255,
                                            shape=(self.channels, self.config['resolution'][0],
                                                   self.config['resolution'][1]),
                                            dtype=np.uint8)

        self.step_output = None
        self.reset()

        self.abs_rotation = 30
        self.abs_horizon = 30


    def step(self, action):
        if not self.action_space.contains(action):
            raise error.InvalidAction('Action must be an integer between '
                                      '0 and {}!'.format(self.action_space.n))
        action_str = self.action_names[action]
        if action_str.startswith('Look'):
            horizon = self.abs_horizon if action_str == 'LookDown' else -self.abs_horizon
            self.step_output = self.controller.step(action='RotateLook', horizon=horizon)
        elif action_str.startswith('Rotate'):
            rotation = self.abs_rotation if action_str == 'RotateRight' else -self.abs_rotation
            self.step_output = self.controller.step(action='RotateLook', rotation=rotation)
        else:
            self.step_output = self.controller.step(action=action_str)

        reward, done = 0, False
        info = {}

        return self.get_observation(), reward, done, info

    def get_observation(self):
        if not self.config['point_cloud_model']:
            frame_img = self.step_output.image_list[0]
            # mask_img = self.step_output.object_mask_list[0]
            obs = torch.from_numpy(self.preprocess(np.array(frame_img))).unsqueeze(0).float()
        else:
            obj_points_feature = self.get_point_cloud(self.step_output)
            agent_info = self.get_agent_info(self.step_output)
            obs = (torch.from_numpy(obj_points_feature).unsqueeze(0).float(),
                   torch.from_numpy(agent_info).unsqueeze(0).float())
        return obs

    def preprocess(self, img):
        """
        Compute image operations to generate state representation
        """
        # TODO: replace scikit image with opencv
        img = transform.resize(img, self.config['resolution'], mode='reflect')
        img = img.astype(np.float32)
        if self.channels == 1:
            img = rgb2gray(img)
        img = np.moveaxis(img, 2, 0)
        return img

    def get_point_cloud(self, event):
        visible_objects = []
        not_visible_objects = []
        for obj in event.metadata['objects']:
            if obj['visible']:
                visible_objects.append(obj)
            else:
                not_visible_objects.append(obj)
        visible_array = np.array(list(map(lambda obj: [obj['position']['x'], obj['position']['y'], obj['position']['z'], 1],
                                   visible_objects))).transpose()
        not_visible_array = np.array(list(map(lambda obj: [obj['position']['x'], obj['position']['y'], obj['position']['z'], 0],
                                   not_visible_objects))).transpose()
        if visible_objects == []:
            cat_array = not_visible_array
        elif not_visible_objects == []:
            cat_array = visible_array
        else:
            cat_array = np.concatenate([visible_array, not_visible_array], axis=1)
        return cat_array

    def get_agent_info(self, event):
        metadata = event.metadata
        position = [metadata['cameraPosition']['x'], metadata['cameraPosition']['y'], metadata['cameraPosition']['z']]
        rotation_x = metadata['agent']['rotation']['x']
        rotation_y = metadata['agent']['rotation']['y']
        rotation_z = metadata['agent']['rotation']['z']
        assert rotation_x == 0
        assert rotation_z == 0
        look_angle = metadata['agent']['cameraHorizon']
        assert round(look_angle) in [-30, 0, 30, 60]
        if look_angle == 330:
            look_angle -= 360
        return np.array(position + [rotation_y * 2 * np.pi / 360] + [look_angle * 2 * np.pi / 360])

    def reset(self):
        # print('Resetting environment and starting new episode')
        self.controller.start_scene(self.scene_config)
        self.step_output = self.controller.step(action='Pass')
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
