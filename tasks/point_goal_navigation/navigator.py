from tasks.task_based_resnet import TaskResNet
from a3c.common import batch_obs, _to_tensor
from tasks.point_goal_navigation.utils import quaternion_rotate_vector, quat_from_angle_axis, normalize_3d_rotation

import numpy as np
from gym.spaces import Box
import machine_common_sense

import torch


class NavigatorResNet(TaskResNet):

    RGB_SENSOR = False
    DEPTH_SENSOR = False

    def __init__(self, action_space):
        super().__init__(self.RGB_SENSOR, self.DEPTH_SENSOR)
        self.goal_sensor_uuid = "pointgoal_with_gps_compass"
        self.observation_spaces.spaces[self.goal_sensor_uuid] = \
            Box(
                low=np.finfo(np.float32).min, high=np.finfo(np.float32).max, dtype=np.float32, shape=(2,)
            )

        self.set_up_resnet_actor_critic(action_space, self.goal_sensor_uuid)
        self.goal = None

    def get_observation(self, step_output):
        obs = {}
        theta = self.get_polar_direction(self.goal, step_output)
        obs[self.goal_sensor_uuid] = np.array([self.distance_to_goal(self.goal, step_output), theta])
        if self.RGB_SENSOR:
            frame_img = self.preprocess(step_output.image_list[0], 'rgb')
            obs['rgb'] = frame_img
        if self.DEPTH_SENSOR:
            depth_img = self.preprocess(step_output.depth_mask_list[0], 'depth')
            obs['depth'] = depth_img
        return [obs]

    def set_goal(self, goal):
        self.goal = goal

    @staticmethod
    def distance_to_goal(goal, step_output):
        distance = (
                        (step_output.position['x'] - goal[0]) ** 2 + \
                        (step_output.position['z'] - goal[2]) ** 2
        ) ** 0.5

        return distance

    @staticmethod
    def get_polar_direction(goal, step_output):
        delta_x_3d = goal[0] - step_output.position['x']
        delta_y_3d = goal[1] - step_output.position['y']
        delta_z_3d = goal[2] - step_output.position['z']
        delta_x_unit_3d, delta_y_unit_3d, delta_z_unit_3d = normalize_3d_rotation(delta_x_3d, delta_y_3d, delta_z_3d)
        # the agent is originally looking at z axis
        # rotate_state = degrees of rotating right

        theta = 2 * np.pi * step_output.rotation / 360
        souce_rotation = quat_from_angle_axis(theta)
        direction_vec_unit = [delta_x_unit_3d, delta_y_unit_3d, delta_z_unit_3d]
        direction_vec_unit_agent = quaternion_rotate_vector(souce_rotation.inverse(), direction_vec_unit)
        dir_3d = np.arctan2(-direction_vec_unit_agent[0], direction_vec_unit_agent[2])

        # theta = 2 * np.pi * step_output.rotation / 360
        # reverse_rotate_complex = np.array(np.cos(theta) + np.sin(theta) * 1j)
        # delta_x_unit_2d, _, delta_z_unit_2d = normalize_3d_rotation(delta_x_unit_3d, 0, delta_z_unit_3d)
        # relative_complex = np.array(delta_z_unit_2d - delta_x_unit_2d * 1j)
        # rotate_direction = relative_complex * reverse_rotate_complex
        # dir_2d = np.arctan2(rotate_direction.imag, rotate_direction.real)
        # print(dir_3d, dir_2d)
        return dir_3d

    def print_target_info(self, step_output):
        print(
            'Goal: {}, Distance_XZ: {}, Direction: {}'.format(
                self.goal,
                self.distance_to_goal(self.goal, step_output),
                self.get_polar_direction(self.goal, step_output),
            )
        )

    def go_to_goal(self, env, goal, success_distance, epsd_collector=None, frame_colletor=None):
        assert success_distance is not None
        self.set_goal(goal)
        done = False
        mask = torch.zeros(size=(1,1))
        hidden_states = torch.zeros(size=(self.actor_critic.net.num_recurrent_layers,1,512))
        prev_action = torch.zeros(1,1)
        obs = self.get_observation(env.step_output)
        step_cnt = 0
        while not done:
            batch = batch_obs(obs)
            action_int, hidden_states = self.act(batch, hidden_states, prev_action, mask, deterministic=False)
            prev_action.copy_(_to_tensor(action_int))
            mask = torch.ones(size=(1,1))
            step_output = env.step(env.action_names[action_int], epsd_collector, frame_colletor)
            obs = self.get_observation(step_output)
            done = self.distance_to_goal(self.goal, step_output) < success_distance
            step_cnt += 1
            if step_cnt > 2000:
                return False
        return True

    def navigation_step_with_reward(self, env, action_int, reach_max_length):
        reward = -0.01
        done = False
        previous_distance = NavigatorResNet.distance_to_goal(self.goal, env.step_output)
        previous_xz = (env.step_output.position['x'], env.step_output.position['z'])
        env.step(env.action_names[action_int])
        new_distance = NavigatorResNet.distance_to_goal(self.goal, env.step_output)
        new_xz = (env.step_output.position['x'], env.step_output.position['z'])
        reward += (previous_distance - new_distance)
        if env.action_names[action_int] == "Stop":
            done = True
            if new_distance < machine_common_sense.mcs_controller_ai2thor.MAX_REACH_DISTANCE:
                reward += 10
        elif env.action_names[action_int] == "MoveAhead":
            move_amount = ((previous_xz[0] - new_xz[0]) ** 2 + (previous_xz[1] - new_xz[1]) ** 2) ** 0.5
            if abs(move_amount - 0.25) > 1e-3:
                # reward -= 10
                done = True
        done = done or reach_max_length
        return reward, done



















