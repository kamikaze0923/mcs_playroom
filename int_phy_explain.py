from gym_ai2thor.envs.mcs_env import McsEnv
from int_phy.scene_state import SceneState
from int_phy.checker import ApearanceModel, LocomotionModel


# scene_name = "github_scenes" + "/problem"
scene_name = "validation_intphys_scenes/shape_constancy"
# scene_name = "validation_intphys_scenes/spatio_temporal_continuity"
scene_name = "github_scenes/shape_constancy"
# scene_name = "shape_constancy"
scene_name = "validation_intphys_scenes/object_permanence"
start_scene_number = 0
env = McsEnv(task="intphys_scenes", scene_type=scene_name, start_scene_number=start_scene_number)

appearance_checker = ApearanceModel()
locomotion_checker = LocomotionModel()

for scene in range(len(env.all_scenes) - start_scene_number):
    env.reset(random_init=False)
    scene_state = SceneState(env.step_output, plot=True)
    for i, x in enumerate(env.scene_config['goal']['action_list']):
        env.step(action=x[0])
        if env.step_output is None:
            break
        scene_state.update(env.step_output, appearance_checker, locomotion_checker)

    final_score = scene_state.get_final_score()
    if 'answer' in env.scene_config:
        if env.scene_config['answer']['choice'] == "plausible":
            if final_score != 1:
                print(env.scene_config['answer']['choice'])
                print("Scene appearance score: {}".format(scene_state.get_scene_appearance_scrore()))
                print("Scene locomotion score: {}".format(scene_state.get_scene_locomotion_score()))
        else:
            if final_score != 0:
                print(env.scene_config['answer']['choice'])
                print("Scene appearance score: {}".format(scene_state.get_scene_appearance_scrore()))
                print("Scene locomotion score: {}".format(scene_state.get_scene_locomotion_score()))

    if final_score == 1:
        choice = "plausible"
        confidence = final_score
    else:
        choice = "implausible"
        confidence = 1 - final_score
    env.controller.end_scene(choice, confidence)



