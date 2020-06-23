from gym_ai2thor.envs.mcs_env import McsEnv
from int_phy.locomotion.network import ObjectStatePrediction, HIDDEN_STATE_SIZE
from int_phy_recollect_position import get_locomotion_feature
from int_phy.locomotion.train import MODEL_SAVE_DIR
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.lines import Line2D
matplotlib.use('MacOSX')
import torch
import os


scene_name = "object_permanence"

net = ObjectStatePrediction()
net.eval()
net.load_state_dict(
    torch.load(os.path.join(MODEL_SAVE_DIR, "model_{}_hidden_state.pth".format(HIDDEN_STATE_SIZE)), map_location="cpu")
)

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
            Line2D([0], [0], marker='o', color='w', markerfacecolor='b', label='Model Prediction', markersize=5),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='r', label='Ground Truth', markersize=5)
        ]
        plt.legend(handles=legend_elements, prop={'size': 6})
        plt.pause(0.01)
        env_1.scene_config['objects'] = [one_obj] + env_occluders

        env_1.step_output = env_1.controller.start_scene(env_1.scene_config)

        h_t = torch.zeros(size=(1, 1, HIDDEN_STATE_SIZE))
        c_t = torch.zeros(size=(1, 1, HIDDEN_STATE_SIZE))
        print(len(env_1.scene_config['goal']['action_list']))

        obj_in_scene = 0
        object_pred_leave = False
        for i, action in enumerate(env_1.scene_config['goal']['action_list']):
            env_1.step(action=action[0])

            obj_in_view = None
            if len(env_1.step_output.object_list) == 1:
                obj_in_scene += 1
                f_1 = get_locomotion_feature(env_1.step_output, object_occluded=False, object_in_scene=obj_in_scene > 0)
                obj_in_view = True
            elif len(env_1.step_output.object_list) == 0:
                f_1 = get_locomotion_feature(None, object_occluded=True, object_in_scene=obj_in_scene > 0)
                obj_in_view = False
                if obj_in_scene > 0:
                    obj_in_scene += 1

            gx, gy = f_1[0], f_1[1]

            # update hidden state
            f_1 = f_1.detach().clone().unsqueeze(0).unsqueeze(0)
            output_1, (h_t, c_t)  = net((f_1, h_t, c_t))
            pred_position, pred_prob_leave = output_1


            pred_position = pred_position.detach().numpy().squeeze()
            px, py = pred_position[0], pred_position[1]
            pred_prob_leave = pred_prob_leave.item()


            # plot the ground truth
            if obj_in_scene > 0 and obj_in_view:
                plt.scatter(gx, gy, s=5, color='r')
                plt.annotate("{}".format(obj_in_scene), (gx, gy), size=5)
                plt.pause(0.1)

            # plot next step's prediction
            if obj_in_scene > 0:
                if pred_prob_leave < 0.9 and not object_pred_leave:
                    plt.scatter(px, py, s=5, color='b')
                    plt.annotate("{}".format(obj_in_scene+1), (px, py), size=5)
                    plt.pause(0.1)
                else:
                    if not object_pred_leave:
                        print("Next step leave scene prob {}".format(pred_prob_leave))
                        object_pred_leave = True

        plt.close()


env_1.controller.end_scene(None, None)



