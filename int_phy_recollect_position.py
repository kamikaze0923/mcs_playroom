from gym_ai2thor.envs.mcs_env import McsEnv
import torch
import os, sys


# SCENE_TYPES = ["object_permanence", "shape_constancy", "spatio_temporal_continuity"]
SCENE_TYPES = ["object_permanence", "shape_constancy"]
SHAPE_TYPES = ["cylinder", "sphere", "cube"]

WITH_OCCLUDER = False
SAVE_SCENE_LENGTH = 40

TOTAL_SCENE = 1080 # max 1080
assert TOTAL_SCENE % SAVE_SCENE_LENGTH == 0
N_RESTART = TOTAL_SCENE // SAVE_SCENE_LENGTH



def get_locomotion_feature(obj, object_occluded, object_in_scene):
    features = []
    if not object_in_scene:
        features.extend([0.0]*29)
    else:
        if object_occluded:
            features.extend([.0] * 28)
            features.extend([1.0])
        else:
            features.append(obj.position['x'])
            features.append(obj.position['y'])
            features.append(obj.position['z'])
            for bonding_vertex in obj.dimensions:
                features.append(bonding_vertex['x'])
                features.append(bonding_vertex['y'])
                features.append(bonding_vertex['z'])
            features.extend([0.0,1.0])

    assert len(features) == 29
    return torch.tensor(features)


if __name__ == "__main__":

    for scene_type in all_scene:
        for _, shape_type in enumerate(SHAPE_TYPES):
            if WITH_OCCLUDER:
                os.makedirs(os.path.join("appearance", "locomotion", "with_occluder", shape_type, scene_type), exist_ok=True)
            else:
                os.makedirs(os.path.join("appearance", "locomotion", "without_occluder", shape_type, scene_type), exist_ok=True)
            object_locomotions = {}

        start_scene_number = 0
        for n_restart in range(N_RESTART):

            object_locomotions = {}
            for _, shape_type in enumerate(SHAPE_TYPES):
                object_locomotions[shape_type] = []

            env = McsEnv(task="intphys_scenes", scene_type=scene_type, start_scene_number=start_scene_number)
            start_scene_number += SAVE_SCENE_LENGTH
            for _ in range(SAVE_SCENE_LENGTH):
                env.reset(random_init=False)
                env_new_objects = []
                env_occluders = []
                for obj in env.scene_config['objects']:
                    if "occluder" not in obj['id']:
                        env_new_objects.append(obj)
                    else:
                        env_occluders.append(obj)
                for one_obj in env_new_objects:
                    if WITH_OCCLUDER:
                        env.scene_config['objects']  = [one_obj] + env_occluders
                    else:
                        env.scene_config['objects'] = [one_obj]
                    env.step_output = env.controller.start_scene(env.scene_config)
                    one_episode_locomotion = []
                    object_in_scene = False
                    for i, action in enumerate(env.scene_config['goal']['action_list']):
                        env.step(action=action[0])
                        if len(env.step_output.object_list) == 1:
                            object_in_scene = True
                            object_occluded = False
                            one_episode_locomotion.append(get_locomotion_feature(env.step_output.object_list[0], object_occluded, object_in_scene))
                        elif len(env.step_output.object_list) == 0:
                            if not WITH_OCCLUDER:
                                object_in_scene = False
                                object_occluded = False
                            else:
                                object_in_scene = True
                                object_occluded = True
                            one_episode_locomotion.append(get_locomotion_feature(None, object_occluded, object_in_scene))
                        else:
                            print("Error!")
                            exit(0)
                    print("Locomotion length: {}".format(len(one_episode_locomotion)))
                    one_episode_locomotion = torch.stack(one_episode_locomotion)
                    object_locomotions[one_obj['type']].append(one_episode_locomotion)

            for _, shape_type in enumerate(SHAPE_TYPES):
                all_seq_len = [t.size()[0] for t in object_locomotions[shape_type]]
                if len(all_seq_len) == 0:
                    continue
                print(shape_type)
                max_locomotion_length = max(all_seq_len)
                padded_locomotion = torch.zeros(
                    size=
                    (
                        len(object_locomotions[shape_type]), max_locomotion_length,
                        object_locomotions[shape_type][0].size()[1]
                    )
                )
                print(padded_locomotion.size())
                for i, x in enumerate(object_locomotions[shape_type]):
                    padded_locomotion[i, -x.size()[0]:, :] = x
                if WITH_OCCLUDER:
                    torch.save(padded_locomotion, os.path.join("appearance", "locomotion", "with_occluder", shape_type, scene_type, "{}.pth".format(n_restart)))
                else:
                    torch.save(padded_locomotion, os.path.join("appearance", "locomotion", "without_occluder", shape_type, scene_type, "{}.pth".format(n_restart)))

            env.controller.end_scene(None, None)






