from gym_ai2thor.envs.mcs_env import McsEnv
from metaController.metaController import MetaController



if __name__ == "__main__":
    env = McsEnv()
    # metaController = MetaController(env)
    # result = metaController.excecute()
    # exit(0)



    for i in range(5, len(env.all_scenes)):
        print(i)
        metaController = MetaController(env)
        result = metaController.excecute()
        env.reset()

