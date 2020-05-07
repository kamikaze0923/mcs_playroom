from gym_ai2thor.envs.mcs_env import McsEnv
from metaController.metaController import MetaController
import sys


if __name__ == "__main__":
    env = McsEnv(interaction_sceces="traversal")
    env.reset()
    # metaController = MetaController(env)
    # result = metaController.excecute()
    # exit(0)

    while env.current_scence <= len(env.all_scenes):
        print(env.current_scence)
        metaController = MetaController(env)
        result = metaController.excecute()
        sys.stdout.flush()
        env.reset()

