from gym_ai2thor.envs.mcs_env import McsEnv
from int_phy.scene_state import SceneState
import matplotlib.pyplot as plt

scene_name = "object_permanence"
start_scene_number = 3
env = McsEnv(task="intphys_scenes", scene_type=scene_name, start_scene_number=start_scene_number)

object_states = []

for _ in range(1):
    env.reset(random_init=False)
    # print(env.current_scene, env.scene_config['answer'], len(env.scene_config['goal']['action_list']))
    scene_state = None
    for i, x in enumerate(env.scene_config['goal']['action_list']):
        # print(i)
        if i == 0:
            scene_state = SceneState(env.step_output)
        else:
            scene_state.update(env.step_output)
        env.step(action=x[0])

    object_states.append(scene_state)
    env.controller.end_scene(None, None)

for i, scene_state in enumerate(object_states):
    plt.figure()
    for j, (id, obj_state) in enumerate(scene_state.object_state_dict.items()):
        v_xs = [v[0] for v in obj_state.velocity_history]
        v_ys = [v[1] for v in obj_state.velocity_history]
        plt.scatter(v_xs, v_ys, label="Object {}".format(j), alpha=0.3, edgecolors='none')

    plt.title("{} scene {} velocity distribution".format(scene_name, i+start_scene_number))
    plt.xlabel("velocity_x")
    plt.ylabel("velocity_y")
    plt.legend()
    plt.savefig("int_phy/velocity/{}/{}".format(scene_name, i+start_scene_number))
    plt.close()
