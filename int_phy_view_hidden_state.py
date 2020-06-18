from gym_ai2thor.envs.mcs_env import McsEnv
from locomotion.network import ObjectStatePrediction, HIDDEN_STATE_SIZE, NUM_HIDDEN_LAYER
from locomotion.train import MODEL_SAVE_DIR
from int_phy_recollect_position import get_locomotion_feature
import matplotlib.pyplot as plt
import torch
import os

scene_name = "object_permanence"
start_scene_number = 0
env = McsEnv(task="intphys_scenes", scene_type=scene_name, start_scene_number=start_scene_number)

net = ObjectStatePrediction()
net.eval()
net.load_state_dict(torch.load(os.path.join(MODEL_SAVE_DIR, "model_{}layerGRU.pth".format(NUM_HIDDEN_LAYER))))

colors = ['ob', 'og', 'or', 'oc']

for _ in range(30):
    env.reset(random_init=False)
    n_object_hidden_state = {obj['id']:[] for obj in env.scene_config['objects'] if "occluder" not in obj['id']}
    obj_seen = {obj['id']:False for obj in env.scene_config['objects'] if "occluder" not in obj['id']}
    axis = []
    for key in n_object_hidden_state.keys():
        ax = plt.figure(figsize=(4,4))
        plt.title("Object {} hidden state".format(key))
        plt.pause(0.5)
        axis.append(ax)

    h_t = torch.zeros(size=(NUM_HIDDEN_LAYER, 1, HIDDEN_STATE_SIZE))
    assert len(env.scene_config['goal']['action_list']) == 40 or len(env.scene_config['goal']['action_list']) == 60
    if len(env.scene_config['goal']['action_list']) == 40:
        env.scene_config['goal']['action_list'] = [["Pass"] for _ in range(20)] + env.scene_config['goal']['action_list']


    h_t = [h_t for _ in range(len(axis))]

    for _, x in enumerate(env.scene_config['goal']['action_list']):
        env.step(action=x[0])

        for i, obj_id in enumerate(n_object_hidden_state.keys()):
            obj = list(filter(lambda x: x.uuid == obj_id, env.step_output.object_list))
            if len(obj) == 0:
                feature = get_locomotion_feature(None)
            else:
                assert len(obj) == 1
                obj_seen[obj_id] = True
                feature = get_locomotion_feature(obj[0])
            feature = torch.tensor(feature)
            feature = feature.unsqueeze(0).unsqueeze(0)
            h_t[i], _ = net((feature, h_t[i]))
            h_t_numpy = h_t[i].detach().numpy().squeeze()
            plt.figure(axis[i].number)
            if obj_seen[obj_id]:
                plt.plot(h_t_numpy[0], h_t_numpy[1], colors[i])
                plt.pause(0.5)
            n_object_hidden_state[obj_id].append(h_t[i])

    for ax in axis:
        plt.figure(ax.number)
        plt.close()
        plt.pause(0.5)




env.controller.end_scene(None, None)


