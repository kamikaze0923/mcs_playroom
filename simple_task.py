from gym_ai2thor.envs.mcs_env import McsEnv
from metaController.metaController import MetaController



if __name__ == "__main__":
    env = McsEnv()
    for i in range(len(env.all_scenes)):
        print(i)
        metaController = MetaController(env)
        result = metaController.excecute()
        env.reset()

