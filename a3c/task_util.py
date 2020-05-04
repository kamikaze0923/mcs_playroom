from gym_ai2thor.envs.mcs_nav import McsNavWrapper
from point_goal_navigation.navigator import NavigatorResNet

def get_model_from_task(env, task_name):
    if task_name == "point_goal_navigation":
        nav_env = McsNavWrapper(env)
        navigator = NavigatorResNet(nav_env.action_space, "pointgoal_with_gps_compass")
        return nav_env, navigator, navigator.actor_critic
