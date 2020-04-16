from point_goal_navigation.model.policy import PointNavResNetPolicy
from point_goal_navigation.common.utils import batch_obs, _to_tensor
from point_goal_navigation.common.utils import quaternion_rotate_vector, quat_from_angle_axis, normalize_3d_rotation

import numpy as np
from skimage import transform
from gym.spaces import Box

import torch

class ObeserationSpace:
    def __init__(self):
        self.spaces = {}

class NavigatorResNet:

    RGB_SENSOR = False
    DEPTH_SENSOR = False
    RESOLUTION = (256, 256)

    def __init__(self, action_space, goal_sensor_uuid):
        self.observation_spaces = ObeserationSpace()
        self.observation_spaces.spaces['pointgoal_with_gps_compass'] = Box(
                low=np.finfo(np.float32).min, high=np.finfo(np.float32).max,
                dtype=np.float32, shape=(2,)
            )

        if self.RGB_SENSOR:
            self.observation_spaces.spaces['rgb'] = Box(low=0, high=255, dtype=np.uint8,
                                                        shape=(self.RESOLUTION[0], self.RESOLUTION[1], 3)
                                                        )
        if self.DEPTH_SENSOR:
            self.observation_spaces.spaces['depth'] = Box(low=0, high=255, dtype=np.uint8,
                                                          shape=(self.RESOLUTION[0], self.RESOLUTION[1], 1)
                                                          )
        self.actor_critic = PointNavResNetPolicy(
            self.observation_spaces,
            action_space,
            goal_sensor_uuid
        )
        self.goal = None


    def act(self, obs, hidden_states, prev_action, mask):
        _, action, _, rnn_hidden_states = self.actor_critic.act(obs, hidden_states, prev_action, mask, deterministic=False)
        return action[0].item(), rnn_hidden_states

    def load_checkpoint(self, checkpoint_path):
        ckpt = torch.load(checkpoint_path, map_location='cpu')
        self.actor_critic.load_state_dict(
            {
                k[len("actor_critic."):]: v
                for k, v in ckpt["state_dict"].items()
                if "actor_critic" in k
            },
            strict=False
        )

    def preprocess(self, img):
        img = np.array(img)
        if len(img.shape) == 2:
            img = np.expand_dims(img, axis=-1)
        img = transform.resize(img, self.observation_spaces, mode='reflect')
        img = img.astype(np.float32)
        return img

    def get_observation(self, step_output):
        obs = {}
        theta = self.get_polar_direction(self.goal, step_output)
        obs['pointgoal_with_gps_compass'] = np.array([self.distance_to_goal(self.goal, step_output), theta])
        if self.RGB_SENSOR:
            frame_img = self.preprocess(step_output.image_list[0])
            obs['rgb'] = frame_img
        if self.DEPTH_SENSOR:
            depth_img = self.preprocess(step_output.depth_mask_list[0]) / 2
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

        # theta = 2 * np.pi * self.rotation_state / 360
        # souce_rotation = quat_from_angle_axis(theta)
        # direction_vec_unit = [delta_x_unit_3d, delta_y_unit_3d, delta_z_unit_3d]
        # direction_vec_unit_agent = quaternion_rotate_vector(souce_rotation.inverse(), direction_vec_unit)
        # dir_3d = np.round(np.arctan2(-direction_vec_unit_agent[0], direction_vec_unit_agent[2]), 2)

        theta = 2 * np.pi * step_output.rotation / 360
        reverse_rotate_complex = np.array(np.cos(theta) + np.sin(theta) * 1j)
        delta_x_unit_2d, _, delta_z_unit_2d = normalize_3d_rotation(delta_x_unit_3d, 0, delta_z_unit_3d)
        relative_complex = np.array(delta_z_unit_2d - delta_x_unit_2d * 1j)
        rotate_direction = relative_complex * reverse_rotate_complex
        dir_2d = np.round(np.arctan2(rotate_direction.imag, rotate_direction.real), 2)
        # print(dir_3d, dir_2d)
        return dir_2d

    def print_target_info(self, step_output):
        print(
            'Goal: {}, Distance_XZ: {}, Direction: {}'.format(
                self.goal,
                self.distance_to_goal(self.goal, step_output),
                self.get_polar_direction(self.goal, step_output),
            )
        )

    def go_to_goal(self, env, goal):
        self.set_goal(goal)
        done = False
        mask = torch.zeros(size=(1,1))
        hidden_states = torch.zeros(size=(self.actor_critic.net.num_recurrent_layers,1,512))
        prev_action = torch.zeros(1,1)
        obs = self.get_observation(env.step_output)
        while not done:
            batch = batch_obs(obs)
            action, hidden_states = self.act(batch, hidden_states, prev_action, mask)
            prev_action.copy_(_to_tensor(action))
            mask = torch.ones(size=(1,1))
            step_output = env.step(action)
            obs = self.get_observation(step_output)
            done = self.distance_to_goal(self.goal, step_output) <= env.max_reach_distance - 0.8














