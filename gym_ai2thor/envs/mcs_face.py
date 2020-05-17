from gym_ai2thor.envs.mcs_wrapper import McsWrapper
from tasks.point_goal_navigation.navigator import NavigatorResNet
import numpy as np

CAMERA_HIGHT = 2

class McsFaceWrapper(McsWrapper):

    ABS_HEADTILT = 10
    ABS_ROTATION = 10 # same as settings in habitat, right is positive
    ABS_MOVE = 0.1

    def __init__(self, env):
        super().__init__(env)

        self.action_names = [
            "MoveAhead", "MoveBack", "MoveLeft", "MoveRight", "RotateLeft", "RotateRight", "LookUp", "LookDown", "Stop"
        ]

    def step(self, action, epsd_collector=None):
        assert action in self.action_names
        if action == "LookUp":
            super().step(action="RotateLook", horizon=-self.ABS_HEADTILT)
        elif action == "LookDown":
            super().step(action="RotateLook", horizon=self.ABS_HEADTILT)
        elif action == "RotateLeft":
            super().step(action="RotateLook", rotation=-self.ABS_ROTATION)
        elif action == "RotateRight":
            super().step(action="RotateLook", rotation=self.ABS_ROTATION)
        elif action == "MoveAhead":
            super().step(action="MoveAhead", amount=self.ABS_MOVE)
        elif action == "MoveBack":
            super().step(action="MoveBack", amount=self.ABS_MOVE)
        elif action == "MoveLeft":
            super().step(action="MoveLeft", amount=self.ABS_MOVE)
        elif action == "MoveRight":
            super().step(action="MoveRight", amount=self.ABS_MOVE)
        if epsd_collector is not None:
            epsd_collector.add_experience(self.step_output, action)

    def set_look_dir(self, rotation_in_all, horizon_in_all):
        super().step(action="RotateLook", horizon=horizon_in_all, rotaion=rotation_in_all)






