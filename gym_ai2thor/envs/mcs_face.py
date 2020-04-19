from gym_ai2thor.envs.mcs_wrapper import McsWrapper
from point_goal_navigation.navigator import NavigatorResNet
import numpy as np

CAMERA_HIGHT = 2

class McsFaceWrapper(McsWrapper):

    MICRO_ROTATION = 10
    MICRO_HEADTILT = 10
    MICRO_MOVE = 0.1

    def __init__(self, env):
        super().__init__(env)

        self.action_names = {
            "w": "MoveAhead", "s": "MoveBack", "a": "MoveLeft", "d": "MoveRight",
            "q": "RotateLeft", "e": "RotateRight", "r": "LookUp", "f": "LookDown"
        }

    def step(self, dir):
        action = self.action_names[dir]
        assert dir in self.action_names
        if action == "LookUp":
            super().step(action="RotateLook", horizon=-self.MICRO_HEADTILT)
        elif action == "LookDown":
            super().step(action="RotateLook", horizon=self.MICRO_HEADTILT)
        elif action == "RotateLeft":
            super().step(action="RotateLook", rotation=-self.MICRO_ROTATION)
        elif action == "RotateRight":
            super().step(action="RotateLook", rotation=self.MICRO_ROTATION)


    def look_to_front(self):
        while abs(self.step_output.head_tilt) > self.MICRO_HEADTILT:
            if self.step_output.head_tilt  > 0:
                self.step("r")
            else:
                self.step("f")

    def look_to_direction(self, goal):
        while True:
            theta = NavigatorResNet.get_polar_direction(goal, self.step_output)
            if abs(theta * 360 / (2 * np.pi)) < self.MICRO_ROTATION:
                break
            if theta > 0:
                self.step("q")
            else:
                self.step("e")

        while True:
            omega = self.get_head_tilt(goal, self.step_output)
            diff = omega - self.step_output.head_tilt
            if diff < self.MICRO_HEADTILT:
                break
            if diff > 0:
                self.step("f")
            else:
                self.step("r")

    @staticmethod
    def get_head_tilt(goal, step_output):
        distance_to_goal = NavigatorResNet.distance_to_goal(goal, step_output) + 1e-6
        delta_y = step_output.position['y'] - goal[1]
        return np.arctan(delta_y/distance_to_goal) * 360 / (2 * np.pi)




