from gym_ai2thor.envs.mcs_env import McsEnv
from metaController.meta_controller import MetaController


from frame_colletor import FrameCollector
from array2gif import write_gif

if __name__ == "__main__":
    c = FrameCollector()

    env = McsEnv(task="interaction_scenes", scene_type="retrieval", start_scene_number=0)
    metaController = MetaController(env)

    while env.current_scene < len(env.all_scenes) - 1:
        env.reset()
        print(env.current_scene)
        metaController.get_inital_planner_state()
        result = metaController.excecute()
        break
    # print(len(c.frames))
    # write_gif(c.frames, 'original.gif', fps=5)


