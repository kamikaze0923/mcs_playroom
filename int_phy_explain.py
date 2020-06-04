from gym_ai2thor.envs.mcs_env import McsEnv
from int_phy.scene_state import SceneState


scene_name = "github_scenes" + "/shape_constancy"
start_scene_number = 2
env = McsEnv(task="intphys_scenes", scene_type=scene_name, start_scene_number=start_scene_number)

for scene in range(len(env.all_scenes) - start_scene_number):
    print("Scene: {}".format(scene + start_scene_number))
    env.reset(random_init=False)
    scene_state = SceneState(env.step_output)
    for i, x in enumerate(env.scene_config['goal']['action_list']):
        # print(i)
        env.step(action=x[0])
        if env.step_output is None:
            break
        scene_state.update(env.step_output)

    env.controller.end_scene(None, None)
