from gym_ai2thor.envs.mcs_env import McsEnv
from int_phy.object_state import ObjectState, pre_process_cropped_img, IMAGE_CROP_SIZE, get_object_match_pixels
from PIL import Image
import numpy as np
import torch
import os, sys

SHAPE_TYPES = ["cylinder", "sphere", "cube"]
all_scene = ["object_permanence", "shape_constancy", "spatio_temporal_continuity"]


def get_locomotion_feature(obj):
    features = []
    if obj is None:
        features.extend([.0]*28)
    else:
        features.append(obj.position['x'])
        features.append(obj.position['y'])
        features.append(obj.position['z'])
        for bonding_vertex in obj.dimensions:
            features.append(bonding_vertex['x'])
            features.append(bonding_vertex['y'])
            features.append(bonding_vertex['z'])
        features.append(1)
    assert len(features) == 28
    return torch.tensor(features)


if __name__ == "__main__":

    object_locomotions = {}
    for _, shape_type in enumerate(SHAPE_TYPES):
        os.makedirs(os.path.join("appearance", "locomotion", shape_type), exist_ok=True)
        object_locomotions[shape_type] = []

    for scene_name in all_scene:
        env = McsEnv(task="intphys_scenes", scene_type=scene_name, start_scene_number=0)
        while env.current_scene < len(env.all_scenes) - 1:
            env.reset(random_init=False)
            env_new_objects = []
            env_occluders = []
            for obj in env.scene_config['objects']:
                if "occluder" not in obj['id']:
                    env_new_objects.append(obj)
                else:
                    env_occluders.append(obj)
            for one_obj in env_new_objects:
                if one_obj['type'] != SHAPE_TYPES[0]:
                    continue
                env.scene_config['objects']  = [one_obj] + env_occluders
                env.step_output = env.controller.start_scene(env.scene_config)
                one_episode_locomotion = []
                for i, action in enumerate(env.scene_config['goal']['action_list']):
                    env.step(action=action[0])
                    if len(env.step_output.object_list) == 1:
                        one_episode_locomotion.append(get_locomotion_feature(env.step_output.object_list[0]))
                    elif len(env.step_output.object_list) == 0:
                        one_episode_locomotion.append(get_locomotion_feature(None))
                    else:
                        print("Error!")
                        exit(0)
                print("Locomotion length: {}".format(len(one_episode_locomotion)))
                one_episode_locomotion = torch.stack(one_episode_locomotion)
                object_locomotions[one_obj['type']].append(one_episode_locomotion)
        env.controller.end_scene(None, None)

    for _, shape_type in enumerate(SHAPE_TYPES):
        max_locomotion_length = max([t.size()[0] for t in object_locomotions[shape_type]])
        padded_locomotion = torch.zeros(
            size=
            (
                len(object_locomotions[shape_type]), max_locomotion_length, object_locomotions[shape_type][0].size()[1]
            )
        )
        print(padded_locomotion.size())
        for i,x in enumerate(object_locomotions[shape_type]):
            padded_locomotion[i,:x.size()[0],:] = x
        torch.save(padded_locomotion, os.path.join("appearance", "locomotion", shape_type, "0.pth"))




