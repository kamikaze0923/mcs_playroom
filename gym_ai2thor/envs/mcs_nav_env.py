from gym_ai2thor.envs.mcs_env import McsEnv
from gym_ai2thor.utils import read_config

from skimage import transform
from gym.spaces import Box, Discrete
import gym_ai2thor.tasks
import numpy as np



import random

class ObeserationSpace:
    def __init__(self):
        self.spaces = None

class McsNavEnv(McsEnv):
    def __init__(self, config_file='config_files/config_nav.json', config_dict=None):
        super().__init__()

        self.config = read_config(config_file, None)

        all_actions_str = self.all_actions_str
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

        assert 'RotateLook' in all_actions_str
        all_actions_str.remove('RotateLook')
        all_actions_str.append('RotateLeft')
        all_actions_str.append('RotateRight')

        for action in ['MoveLeft', 'MoveRight', 'MoveBack', 'Pass']:
            all_actions_str.remove(action)
        all_actions_str.append('Stop')

        self.action_names = all_actions_str
        self.action_space = Discrete(len(self.action_names))

        self.rgb_sensor = True if self.config['rgb_sensor'] else False
        self.depth_sensor = True if self.config['depth_sensor'] else False

        self.observation_spaces = ObeserationSpace()
        self.observation_spaces.spaces = {
            'point_goal_with_gps_compass': Box(
                low=np.finfo(np.float32).min, high=np.finfo(np.float32).max,
                dtype=np.float32, shape=(2,)
            )
        }
        if self.rgb_sensor:
            self.observation_space['rgb'] = Box(low=0, high=255, dtype=np.uint8,
                                                shape=(3, self.config['resolution'][0], self.config['resolution'][1])
                                            )
        if self.depth_sensor:
            self.observation_space['depth'] = Box(low=0, high=255, dtype=np.uint8,
                                                shape=(1, self.config['resolution'][0], self.config['resolution'][1])
                                            )
        self.rotation_state = 0 # same as MCS internal
        self.abs_rotation = 10 # same as settings in habitat, right is positive

        self.step_output = None
        self.target_object = None
        self.task = None
        self.random_object_no = None
        self.reset()

    def reset(self):
        # print('Resetting environment and starting new episode')
        self.step_output = self.controller.start_scene(self.scene_config)
        n_objects = len(self.step_output.object_list)
        self.random_object_no = random.randint(0, n_objects-1)
        self.random_object_no = 2
        self.target_object = self.step_output.object_list[self.random_object_no]
        self.print_target_info()
        self.task = getattr(gym_ai2thor.tasks, self.config['task']['task_name'])(self.target_object, **self.config)
        return self.get_observation()

    def print_target_info(self):
        print(
            'Target Objext: {}, Direction: {}, Distance: {}, Visible: {}'.format(
                self.target_object.uuid,
                self.get_polar_direction(
                    self.target_object.direction['x'],
                    self.target_object.direction['z']
                ),
                self.target_object.distance,
                self.target_object.visible
            )
        )

    def get_polar_direction(self, delta_x, delta_z):
        # the agent is originally looking at z axis
        # rotate_state = degrees of rotating right
        reverse_theta = 2 * np.pi * self.rotation_state / 360
        relative_complex = np.array(delta_z + delta_x * 1j)
        reverse_rotate_complex = np.array(np.cos(reverse_theta) + np.sin(reverse_theta) * 1j)
        rotate_direction = relative_complex * reverse_rotate_complex
        return np.round(np.arctan2(rotate_direction.imag, rotate_direction.real), 2)

    def step(self, action):
        action_str = self.action_names[action]
        if action_str.startswith('Rotate'):
            rotation = -self.abs_rotation if action_str == 'RotateLeft' else self.abs_rotation
            self.step_output = self.controller.step(action='RotateLook', rotation=rotation)
            self.rotation_state += rotation
        elif action_str == 'MoveAhead':
            self.step_output = self.controller.step(action=action_str, amount=0.25)
        else:
            assert action_str == 'Stop'

        self.target_object = self.step_output.object_list[self.random_object_no]

        reward, done = self.task.transition_reward((self.target_object, action_str))
        info = {}
        self.print_target_info()

        return self.get_observation(), reward, done, info

    def get_observation(self):
        obs = {}
        theta = self.get_polar_direction(self.target_object.direction['x'], self.target_object.direction['z'])
        obs['point_goal_with_gps_compass'] = np.array(self.target_object.distance, theta)
        if self.rgb_sensor:
            frame_img = self.preprocess(self.step_output.image_list[0])
            obs['rgb'] = frame_img
        if self.depth_sensor:
            depth_img = self.preprocess(self.step_output.depth_image_list[0])
            obs['depth'] = depth_img
        return obs

    def preprocess(self, img):
        img = transform.resize(img, self.config['resolution'], mode='reflect')
        img = img.astype(np.float32)
        img = np.moveaxis(img, 2, 0)
        return img