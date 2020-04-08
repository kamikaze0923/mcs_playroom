from gym_ai2thor.envs.mcs_env import McsEnv

from gym.spaces import Discrete
import numpy as np
from point_goal_navigation.common.utils import quaternion_rotate_vector, quat_from_angle_axis, normalize_3d_rotation
from gym_ai2thor.tasks import NavigationToCoordinate
from gym_ai2thor.utils import read_config

import random

class McsNavEnv(McsEnv):
    def __init__(self, nav_config_file='config_files/config_nav.json', config_dict=None):
        super().__init__(config_dict=config_dict)

        self.nav_config = read_config(nav_config_file, config_dict)

        self.nav_action_names = ["Stop", "MoveAhead", "RotateLeft", "RotateRight"]# order matters
        self.nav_action_space = Discrete(len(self.nav_action_names))

        self.task = None


    def nav_reset(self):
        super().reset()
        self.goal = (-2, 0, -2)
        source = (self.step_output.position["x"], self.step_output.position["y"], self.step_output.position["z"])
        self.task = NavigationToCoordinate(source, self.goal, **self.nav_config)
        return self.get_observation()

    def print_target_info(self):
        source = (self.step_output.position["x"], self.step_output.position["y"], self.step_output.position["z"])
        print(
            'Goal: {}, Distance_XZ: {}, Direction: {}'.format(
                self.goal,
                self.task.distance_to_goal(source),
                self.get_polar_direction(
                    self.goal[0] - self.step_output.position['x'],
                    self.goal[1] - self.step_output.position['y'],
                    self.goal[2] - self.step_output.position['z']
                ),
            )
        )

    def get_polar_direction(self, delta_x_3d, delta_y_3d, delta_z_3d):
        delta_x_unit_3d, delta_y_unit_3d, delta_z_unit_3d = normalize_3d_rotation(delta_x_3d, delta_y_3d, delta_z_3d)
        # the agent is originally looking at z axis
        # rotate_state = degrees of rotating right

        # theta = 2 * np.pi * self.rotation_state / 360
        # souce_rotation = quat_from_angle_axis(theta)
        # direction_vec_unit = [delta_x_unit_3d, delta_y_unit_3d, delta_z_unit_3d]
        # direction_vec_unit_agent = quaternion_rotate_vector(souce_rotation.inverse(), direction_vec_unit)
        # dir_3d = np.round(np.arctan2(-direction_vec_unit_agent[0], direction_vec_unit_agent[2]), 2)

        theta = 2 * np.pi * self.rotation_state / 360
        reverse_rotate_complex = np.array(np.cos(theta) + np.sin(theta) * 1j)
        delta_x_unit_2d, _, delta_z_unit_2d = normalize_3d_rotation(delta_x_unit_3d, 0, delta_z_unit_3d)
        relative_complex = np.array(delta_z_unit_2d - delta_x_unit_2d * 1j)
        rotate_direction = relative_complex * reverse_rotate_complex
        dir_2d = np.round(np.arctan2(rotate_direction.imag, rotate_direction.real), 2)
        # print(dir_3d, dir_2d)
        return dir_2d


    def nav_step(self, action):
        action_str = self.nav_action_names[action]
        if action_str.startswith('Rotate'):
            rotation = -self.abs_rotation if action_str == 'RotateLeft' else self.abs_rotation
            self.step_output = self.controller.step(action='RotateLook', rotation=rotation)
            self.rotation_state += rotation
        elif action_str == 'MoveAhead':
            self.step_output = self.controller.step(action=action_str, amount=0.25)
        else:
            assert action_str == 'Stop'

        reward, done = self.task.transition_reward((self.step_output.position, action_str))
        info = {}
        self.print_target_info()

        return self.get_observation(), reward, done, info

    def get_observation(self):
        obs = {}
        theta = self.get_polar_direction(
            self.goal[0] - self.step_output.position['x'],
            self.goal[1] - self.step_output.position['y'],
            self.goal[2] - self.step_output.position['z']
        )
        source = (self.step_output.position["x"], self.step_output.position["y"], self.step_output.position["z"])
        obs['pointgoal_with_gps_compass'] = np.array([self.task.distance_to_goal(source), theta])
        if self.rgb_sensor:
            frame_img = self.preprocess(self.step_output.image_list[0])
            obs['rgb'] = frame_img
        if self.depth_sensor:
            depth_img = self.preprocess(self.step_output.depth_mask_list[0])
            obs['depth'] = depth_img
        return [obs]

