from gym_ai2thor.envs.mcs_env import McsEnv
from meta_ontroller.meta_controller import MetaController
import sys


from frame_colletor import FrameCollector
# from array2gif import write_gif

if __name__ == "__main__":
    # c = FrameCollector()

    env = McsEnv(task="interaction_scenes", scene_type="transferral_on_top_of", start_scene_number=39)
    metaController = MetaController(env)

    while env.current_scene < len(env.all_scenes) - 1:
        env.reset()
        # print(env.current_scene)
        result = metaController.excecute()
        sys.stdout.flush()
    # print(len(c.frames))
    # write_gif(c.frames, 'original.gif', fps=5)


