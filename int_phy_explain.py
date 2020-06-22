from gym_ai2thor.envs.mcs_env import McsEnv
from int_phy.scene_state import SceneState
from int_phy.checker import ApearanceModel, LocomotionModel


# scene_name = "github_scenes" + "/object_permanence"
scene_name = "validation_intphys_scenes/shape_constancy"
# scene_name = "validation_intphys_scenes/shape_constancy"
scene_name = "github_scenes/shape_constancy"
start_scene_number = 0
env = McsEnv(task="intphys_scenes", scene_type=scene_name, start_scene_number=0)

appearance_checker = ApearanceModel()
locomotion_checker = LocomotionModel()

for scene in range(len(env.all_scenes) - start_scene_number):
    env.reset(random_init=False)
    print("Scene: {}".format(scene + start_scene_number))
    if 'answer' in env.scene_config:
        print(env.scene_config['answer'])
    scene_state = SceneState(env.step_output)
    n_object = 3
    for i, x in enumerate(env.scene_config['goal']['action_list']):
        env.step(action=x[0])
        if env.step_output is None:
            break
        scene_state.update(env.step_output, appearance_checker, locomotion_checker)
    print("Scene appearance score: {}".format(scene_state.get_scene_appearance_scrore()))

