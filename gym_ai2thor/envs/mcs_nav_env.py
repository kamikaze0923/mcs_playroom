from gym_ai2thor.envs.mcs_env import McsEnv

from skimage import transform
from gym.spaces import Box, Discrete
import gym_ai2thor.tasks
import numpy as np
from point_goal_navigation.common.utils import quaternion_rotate_vector, quat_from_angle_axis, normalize_3d_rotation




import random

class ObeserationSpace:
    def __init__(self):
        self.spaces = None

class McsNavEnv(McsEnv):
    def __init__(self, config_file='config_files/config_nav.json', config_dict=None):
        super().__init__(config_file, config_dict)

        self.action_names = ["Stop", "MoveAhead", "RotateLeft", "RotateRight"]# order matters
        self.action_space = Discrete(len(self.action_names))

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
        self.rotation_state = None # same as MCS internal
        self.abs_rotation = 10 # same as settings in habitat, right is positive

        self.step_output = None
        self.target_object = None
        self.task = None
        self.random_object_no = None


    def reset(self):
        # self.rotation_state = 0
        # self.scene_config["performerStart"] = {
        #     "position": {
        #         "x": 1,
        #         "z": -3
        #     },
        #     "rotation": {
        #         "y": self.rotation_state
        #     }
        # }
        self.rotation_state = random.sample(self.POSSIBLE_INIT_ROTATION, 1)[0]
        self.scene_config["performerStart"] = {
            "position": {
                "x": random.sample(self.POSSIBLE_INIT_X, 1)[0],
                "z": random.sample(self.POSSIBLE_INIT_Z, 1)[0]
            },
            "rotation": {
                "y": self.rotation_state
            }
        }
        self.step_output = self.controller.start_scene(self.scene_config)
        n_objects = len(self.step_output.object_list)
        self.random_object_no = random.randint(0, n_objects-1)
        # self.random_object_no = 19
        self.target_object = self.step_output.object_list[self.random_object_no]
        # self.print_target_info()
        self.task = getattr(gym_ai2thor.tasks, self.config['task']['task_name'])(self.target_object, **self.config)
        return self.get_observation()

    def print_target_info(self):
        print(
            'Target Objext: {}, Distance: {}, Direction: {}, Visible: {}'.format(
                self.target_object.uuid,
                self.target_object.distance,
                self.get_polar_direction(
                    self.target_object.direction['x'],
                    self.target_object.direction['y'],
                    self.target_object.direction['z']
                ),
                self.target_object.visible
            )
        )

    def get_polar_direction(self, delta_x_3d, delta_y_3d, delta_z_3d, caculation_2d=True):
        # the agent is originally looking at z axis
        # rotate_state = degrees of rotating right

        theta = 2 * np.pi * self.rotation_state / 360
        souce_rotation = quat_from_angle_axis(theta)
        direction_vec_unit = [delta_x_3d, delta_y_3d, delta_z_3d]
        direction_vec_unit_agent = quaternion_rotate_vector(souce_rotation.inverse(), direction_vec_unit)
        dir_3d = np.round(np.arctan2(-direction_vec_unit_agent[0], direction_vec_unit_agent[2]), 2)

        theta = 2 * np.pi * self.rotation_state / 360
        reverse_rotate_complex = np.array(np.cos(theta) + np.sin(theta) * 1j)
        delta_x, delta_z = normalize_3d_rotation(delta_x_3d, delta_z_3d)
        relative_complex = np.array(delta_z - delta_x * 1j)
        rotate_direction = relative_complex * reverse_rotate_complex
        dir_2d = np.round(np.arctan2(rotate_direction.imag, rotate_direction.real), 2)
        # print(dir_3d, dir_2d)
        return dir_2d


    def step(self, action):
        # action = 2
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

        reward, done = self.task.transition_reward((self.target_object.distance, action_str))
        info = {}
        self.print_target_info()

        return self.get_observation(), reward, done, info

    def get_observation(self):
        obs = {}
        theta = self.get_polar_direction(
            self.target_object.direction['x'],
            self.target_object.direction['y'],
            self.target_object.direction['z']
        )
        obs['pointgoal_with_gps_compass'] = np.array([self.target_object.distance, theta])
        if self.rgb_sensor:
            frame_img = self.preprocess(self.step_output.image_list[0])
            obs['rgb'] = frame_img
        if self.depth_sensor:
            depth_img = self.preprocess(self.step_output.depth_mask_list[0])
            obs['depth'] = depth_img
        return [obs]

    def get_rgb(self):
        img = self.step_output.image_list[0].convert(mode="P").convert("RGB")
        img = np.array(img).transpose(2,0,1)
        return img

    def get_depth_rgb(self):
        img1 = self.get_rgb()
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