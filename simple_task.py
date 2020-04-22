from gym_ai2thor.envs.mcs_env import McsEnv
from metaController.metaController import MetaController



if __name__ == "__main__":
    import time
    env = McsEnv()
    metaController = MetaController(env)
    metaController.excecute()

