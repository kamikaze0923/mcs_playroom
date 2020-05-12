from gym_ai2thor.envs.mcs_env import McsEnv
from metaController.metaController import MetaController
import sys


if __name__ == "__main__":
    env = McsEnv(interaction_sceces="traversal")

    while env.current_scene < len(env.all_scenes) - 1:
        env.reset()
        print(env.current_scene)
        metaController = MetaController(env)
        result = metaController.excecute()
        # sys.stdout.flush()


