from gym_ai2thor.envs.mcs_env import McsEnv
from locomotion.network import Position_Embbedding_Network, HIDDEN_STATE_SIZE
from locomotion.train import MODEL_SAVE_DIR
from int_phy_recollect_position import get_locomotion_feature
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.lines import Line2D
matplotlib.use('MacOSX')
import torch
import os
import math

def dis_to_origin(x,y):
    return math.sqrt( x ** 2 + y ** 2)

# scene_name = "github_scenes/spatio_temporal_continuity/implausible"
scene_name = "object_permanence"

net = Position_Embbedding_Network()
net.eval()
net.load_state_dict(torch.load(os.path.join(MODEL_SAVE_DIR, "model_{}_hidden_state.pth".format(HIDDEN_STATE_SIZE))))

start_scene_number = 0
env_1 = McsEnv(task="intphys_scenes", scene_type=scene_name, start_scene_number=start_scene_number)
for _ in range(10):

    env_1.reset(random_init=False)
    env_new_objects = []
    env_occluders = []
    for obj in env_1.scene_config['objects']:
        if "occluder" not in obj['id']:
            env_new_objects.append(obj)
        else:
            env_occluders.append(obj)

    for one_obj in env_new_objects:
        plt.figure(figsize=(6,4))

        plt.xlim((-5, 5))
        plt.ylim((-1, 4))
        plt.title("Position(x,y) of {}".format(one_obj['id']))
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', markerfacecolor='b', label='Model Prediction', markersize=6),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='r', label='Ground Truth', markersize=6)
        ]
        plt.legend(handles=legend_elements, prop={'size': 6})
        plt.pause(0.01)
        env_1.scene_config['objects'] = [one_obj] + env_occluders

        env_1.step_output = env_1.controller.start_scene(env_1.scene_config)

        h_t_1 = torch.zeros(size=(1, 1, HIDDEN_STATE_SIZE))
        print(len(env_1.scene_config['goal']['action_list']))

        if len(env_1.scene_config['goal']['action_list']) == 40:
            for _ in range(20):
                f_none = get_locomotion_feature(None)
                f_none = torch.tensor(f_none)
                f_none = f_none.unsqueeze(0).unsqueeze(0)
                _, h_t_1 = net((f_none, h_t_1))

        obj_in_scene = 0
        for i, action in enumerate(env_1.scene_config['goal']['action_list']):
            env_1.step(action=action[0])

            obj_in_view = None
            if len(env_1.step_output.object_list) == 1:
                f_1 = get_locomotion_feature(env_1.step_output.object_list[0])
                f_1_seen = f_1
                obj_in_view = True
                obj_in_scene += 1
            elif len(env_1.step_output.object_list) == 0:
                f_1 = get_locomotion_feature(None)
                obj_in_view = False

            gx, gy = f_1[0], f_1[1]
            f_1 = torch.tensor(f_1).unsqueeze(0).unsqueeze(0)

            f_1_unseen = get_locomotion_feature(None)
            f_1_unseen = torch.tensor(f_1_unseen).unsqueeze(0).unsqueeze(0)

            #always try what if in next frame obj is unseen
            output_1_unseen, _ = net((f_1_unseen, h_t_1))
            output_1_unseen_numpy = output_1_unseen.detach().numpy().squeeze()

            _, h_t_1 = net((f_1, h_t_1))

            # plot the ground truth
            if obj_in_scene > 0 and obj_in_view:
                plt.plot(gx, gy, "or")
                plt.pause(0.3)

            # after some steps, make a prediction if next step cannot see the object
            if obj_in_scene > 3:
                if dis_to_origin(output_1_unseen_numpy[0], output_1_unseen_numpy[1]) < 1e-1:
                    print("Predict next state out of seen")
                else:
                    plt.plot(output_1_unseen_numpy[0], output_1_unseen_numpy[1], "ob")
                    plt.pause(0.3)



        plt.close()



env_1.controller.end_scene(None, None)



