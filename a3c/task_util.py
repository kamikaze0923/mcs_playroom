from gym_ai2thor.envs.mcs_env import McsEnv
from gym_ai2thor.envs.mcs_nav import McsNavWrapper
from point_goal_navigation.navigator import NavigatorResNet
import subprocess
import shlex

def get_model_from_task(env, task_name):
    if task_name == "point_goal_navigation":
        nav_env = McsNavWrapper(env)
        navigator = NavigatorResNet(nav_env.action_space, "pointgoal_with_gps_compass")
        return nav_env, navigator, navigator.actor_critic


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
