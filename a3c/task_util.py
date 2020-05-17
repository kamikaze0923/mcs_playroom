from gym_ai2thor.envs.mcs_env import McsEnv
from gym_ai2thor.envs.mcs_nav import McsNavWrapper
from gym_ai2thor.envs.mcs_face import McsFaceWrapper
from tasks.point_goal_navigation.navigator import NavigatorResNet
from tasks.search_object_in_receptacle.face_turner import FaceTurnerResNet
import subprocess
import shlex
from gym.spaces import Discrete
import torch

def get_action_space_from_names(action_names):
    return Discrete(len(action_names))

def get_model_from_task(env, task_name):
    if task_name == "point_goal_navigation":
        from tasks.point_goal_navigation.test import test
        from tasks.point_goal_navigation.train import train
        nav_env = McsNavWrapper(env)
        navigator = NavigatorResNet(get_action_space_from_names(nav_env.action_names))
        return nav_env, navigator, navigator.actor_critic, train, test
    elif task_name == "search_object_in_receptacle":
        from tasks.search_object_in_receptacle.test import test
        from tasks.search_object_in_receptacle.train import train
        face_env = McsFaceWrapper(env)
        face_turner = FaceTurnerResNet(get_action_space_from_names(face_env.action_names))
        return face_env, face_turner, face_turner.actor_critic, train, test
    else:
        raise NotImplementedError("task not implemented")


def check_gpu_usage_and_restart_env(env, nav_env):
    command = "nvidia-smi --query-gpu=memory.free --format=csv"
    out = subprocess.check_output(shlex.split(command)).decode("utf-8").split("\n")
    mb_remain = int(out[1].split()[0])
    if mb_remain < 256:
        env.controller.end_scene(None, None)
        new_env = McsEnv()
        new_nav_env = McsNavWrapper(new_env)
    else:
        new_env = env
        new_nav_env = nav_env
    return new_env, new_nav_env
