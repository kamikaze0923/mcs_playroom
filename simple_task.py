from gym_ai2thor.envs.mcs_env import McsEnv
from meta_ontroller.meta_controller import MetaController
import sys


if __name__ == "__main__":
    env = McsEnv(task="interaction_scenes", scene_type="retrieval", start_scene_number=0)
    metaController = MetaController(env)

    while env.current_scene < len(env.all_scenes) - 1:
        env.reset()
        result = metaController.excecute()
        sys.stdout.flush()



