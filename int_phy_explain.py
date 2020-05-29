from gym_ai2thor.envs.mcs_env import McsEnv
from int_phy.scene_state import SceneState


scene_name = "github_scenes"
start_scene_number = 18
env = McsEnv(task="intphys_scenes", scene_type=scene_name, start_scene_number=start_scene_number)

for scene in range(1000):
    print("Scene: {}".format(scene + start_scene_number))
    env.reset(random_init=False)
    # print(env.current_scene, env.scene_config['answer'], len(env.scene_config['goal']['action_list']))
    scene_state = SceneState(env.step_output)
    for i, x in enumerate(env.scene_config['goal']['action_list']):
        print(i)
        env.step(action=x[0])
        if env.step_output is None:
            break
        scene_state.update(env.step_output)

    env.controller.end_scene(None, None)


