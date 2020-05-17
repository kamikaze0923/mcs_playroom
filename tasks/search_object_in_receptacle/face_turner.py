from tasks.task_based_resnet import TaskResNet
from tasks.point_goal_navigation.navigator import NavigatorResNet

import numpy as np
from skimage import transform
from gym.spaces import Box


import torch

class ObeserationSpace:
    def __init__(self):
        self.spaces = {}

class FaceTurnerResNet(TaskResNet):

    RGB_SENSOR = True
    DEPTH_SENSOR = False
    GOAL_IMAGE_RESOLUTION = (64, 64)

    def __init__(self, action_space):
        super().__init__(self.RGB_SENSOR, self.DEPTH_SENSOR)
        self.goal_sensor_uuid = "goal_object_information"
        self.observation_spaces.spaces[self.goal_sensor_uuid] = \
            Box(
                low=0, high=255, dtype=np.uint8, shape=(self.GOAL_IMAGE_RESOLUTION[0], self.GOAL_IMAGE_RESOLUTION[1], 3)
            )

        self.set_up_resnet_actor_critic(
            action_space,
            "goal_object_information",
            goal_object_observation_space=self.observation_spaces.spaces[self.goal_sensor_uuid]
        )

        self.goal_object_image = None
        self.goal_object_id = None

    def set_goal(self, image, goal_object_id):
        self.goal_object_image = self.preprocess_goal_image(image)
        self.goal_object_id = goal_object_id

    def preprocess_goal_image(self, img):
        # if img.shape[0] < self.GOAL_IMAGE_RESOLUTION[0] or img.shape[1] < self.GOAL_IMAGE_RESOLUTION[1]:
        #     import matplotlib.pyplot as plt
        #     plt.imshow(img)
        #     print(img.shape)
        #     exit(0)
        # assert img.shape[0] >= self.GOAL_IMAGE_RESOLUTION[0]
        # assert img.shape[1] >= self.GOAL_IMAGE_RESOLUTION[1]
        if len(img) == 2:
            img = np.expand_dims(img, axis=-1)
        img = img.astype(np.float32) / 255
        img = transform.resize(img, self.observation_spaces.spaces[self.goal_sensor_uuid].shape)
        # img = img * 255
        # img = img.astype(np.uint8)
        # import matplotlib.pyplot as plt
        # plt.imshow(img)
        return img

    def get_observation(self, step_output):
        obs = {}
        obs[self.goal_sensor_uuid] = self.goal_object_image
        if self.RGB_SENSOR:
            frame_img = self.preprocess(step_output.image_list[0], 'rgb')
            obs['rgb'] = frame_img
        if self.DEPTH_SENSOR:
            depth_img = self.preprocess(step_output.depth_mask_list[0], 'depth')
            obs['depth'] = depth_img
        return [obs]

    def object_search_step_with_reward(self, env, action_int, reach_max_length):
        assert self.goal_object_id
        reward = -0.01
        done = False
        env.step(env.action_names[action_int])
        if env.action_names[action_int] == "Stop":
            done = True
            if self.goal_object_id in [obj.uuid for obj in env.step_output.object_list]:
                reward += 1
        done = done or reach_max_length
        return reward, done


    @staticmethod
    def look_to_front(env):
        env.set_look_dir(rotation_in_all=0, horizon_in_all=-env.step_output.head_tilt)

    @staticmethod
    def look_to_direction(env, goal, epsd_collector=None):
        theta = NavigatorResNet.get_polar_direction(goal, env.step_output)
        omega = FaceTurnerResNet.get_head_tilt(goal, env.step_output) - env.step_output.head_tilt
        env.set_look_dir(rotation_in_all=theta, horizon_in_all=omega)

    @staticmethod
    def get_head_tilt(goal, step_output):
        distance_to_goal = NavigatorResNet.distance_to_goal(goal, step_output) + 1e-6
        delta_y = step_output.position['y'] - goal[1]
        return np.arctan(delta_y/distance_to_goal) * 360 / (2 * np.pi)
















