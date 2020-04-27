from gym_ai2thor.envs.mcs_env import McsEnv
from metaController.metaController import MetaController


if __name__ == "__main__":
    env = McsEnv()
    # metaController = MetaController(env)
    # result = metaController.excecute()
    # exit(0)

    while env.current_scence != len(env.all_scenes):
        print(env.current_scence)
        metaController = MetaController(env)
        result = metaController.excecute()
        # assert env.step_output.reward == 1
        env.reset()
