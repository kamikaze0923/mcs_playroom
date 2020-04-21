from gym_ai2thor.envs.mcs_wrapper import McsWrapper
from point_goal_navigation.navigator import NavigatorResNet
import numpy as np

CAMERA_HIGHT = 2

class McsFaceWrapper(McsWrapper):

    def __init__(self, env):
        super().__init__(env)

        self.action_names = {
            "w": "MoveAhead", "s": "MoveBack", "a": "MoveLeft", "d": "MoveRight",
            "q": "RotateLeft", "e": "RotateRight", "r": "LookUp", "f": "LookDown"
        }

    def step(self, dir, epsd_collector=None):
        action = self.action_names[dir]
        assert dir in self.action_names
        if action == "LookUp":
            super().step(action="RotateLook", horizon=-self.ABS_HEADTILT)
        elif action == "LookDown":
            super().step(action="RotateLook", horizon=self.ABS_HEADTILT)
        elif action == "RotateLeft":
            super().step(action="RotateLook", rotation=-self.ABS_ROTATION)
        elif action == "RotateRight":
            super().step(action="RotateLook", rotation=self.ABS_ROTATION)
        if epsd_collector is not None:
            epsd_collector.add_experience(self.step_output, action)


    def look_to_front(self, epsd_collector=None):
        while abs(self.step_output.head_tilt) > self.ABS_HEADTILT:
            if self.step_output.head_tilt  > 0:
                self.step("r", epsd_collector)
            else:
                self.step("f", epsd_collector)


    def look_to_direction(self, goal, epsd_collector=None):
        while True:
            theta = NavigatorResNet.get_polar_direction(goal, self.step_output)
            if abs(theta * 360 / (2 * np.pi)) < self.ABS_ROTATION:
                break
            if theta > 0:
                self.step("q", epsd_collector)
            else:
                self.step("e", epsd_collector)

        while True:
            omega = self.get_head_tilt(goal, self.step_output)
            diff = omega - self.step_output.head_tilt
            if diff < self.ABS_HEADTILT:
                break
            if diff > 0:
                self.step("f", epsd_collector)
            else:
                self.step("r", epsd_collector)

    @staticmethod
    def get_head_tilt(goal, step_output):
        distance_to_goal = NavigatorResNet.distance_to_goal(goal, step_output) + 1e-6
        delta_y = step_output.position['y'] - goal[1]
        return np.arctan(delta_y/distance_to_goal) * 360 / (2 * np.pi)




