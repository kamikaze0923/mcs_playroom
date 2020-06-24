from gym_ai2thor.envs.mcs_env import McsEnv
from int_phy.object_state import get_locomotion_feature
from int_phy.locomotion.datasets import SHAPE_TYPES, SCENE_TYPES, DATA_SAVE_DIR
import torch
import os


WITH_OCCLUDER = False
SAVE_SCENE_LENGTH = 40

TOTAL_SCENE = 40 # max 1080
assert TOTAL_SCENE % SAVE_SCENE_LENGTH == 0
N_RESTART = TOTAL_SCENE // SAVE_SCENE_LENGTH

DATA_SAVE_DIR = os.path.join("int_phy", "locomotion", "positions_old_additional")
SCENE_TYPES = ["shape_constancy", "spatio_temporal_continuity"]


if __name__ == "__main__":
    for scene_type in SCENE_TYPES:
        for _, shape_type in enumerate(SHAPE_TYPES):
            if scene_type == "gravity":
                os.makedirs(os.path.join(DATA_SAVE_DIR, "with_occluder", shape_type, scene_type), exist_ok=True)
                os.makedirs(os.path.join(DATA_SAVE_DIR, "without_occluder", shape_type, scene_type), exist_ok=True)
            else:
                if WITH_OCCLUDER:
                    os.makedirs(os.path.join(DATA_SAVE_DIR, "with_occluder", shape_type, scene_type), exist_ok=True)
                else:
                    os.makedirs(os.path.join(DATA_SAVE_DIR, "without_occluder", shape_type, scene_type), exist_ok=True)

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
                if len(env.scene_config['goal']['action_list']) != 40:
                    continue
                env_new_objects = []
                env_occluders = []
                env_ramps = []
                for obj in env.scene_config['objects']:
                    if "occluder" in obj['id']:
                        env_occluders.append(obj)
                        continue
                    if "ramp" in obj['id']:
                        env_ramps.append(obj)
                        continue
                    if obj['type'] in SHAPE_TYPES:
                        env_new_objects.append(obj)
                for one_obj in env_new_objects:
                    if WITH_OCCLUDER:
                        env.scene_config['objects']  = [one_obj] + env_ramps + env_occluders
                    else:
                        env.scene_config['objects'] = [one_obj] + env_ramps
                    env.step_output = env.controller.start_scene(env.scene_config)
                    one_episode_locomotion = []
                    object_in_scene = False
                    for i, action in enumerate(env.scene_config['goal']['action_list']):
                        env.step(action=action[0])
                        if len(env.step_output.object_list) == 1:
                            object_in_scene = True
                            object_occluded = False
                            one_episode_locomotion.append(get_locomotion_feature(
                                env.step_output, object_occluded, object_in_scene, env.step_output.object_list[0]
                            ))
                        elif len(env.step_output.object_list) == 0:
                            if not WITH_OCCLUDER:
                                object_in_scene = False
                                object_occluded = False
                            else:
                                object_in_scene = True
                                object_occluded = True
                            one_episode_locomotion.append(get_locomotion_feature(None, object_occluded, object_in_scene, None))
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
                        len(object_locomotions[shape_type]), max(max_locomotion_length, 60),
                        object_locomotions[shape_type][0].size()[1]
                    )
                )
                print(padded_locomotion.size())
                for i, x in enumerate(object_locomotions[shape_type]):
                    padded_locomotion[i, -x.size()[0]:, :] = x
                if scene_type == "gravity":
                    torch.save(padded_locomotion, os.path.join(DATA_SAVE_DIR, "with_occluder", shape_type, scene_type, "{}.pth".format(n_restart)))
                    torch.save(padded_locomotion, os.path.join(DATA_SAVE_DIR, "without_occluder", shape_type, scene_type, "{}.pth".format(n_restart)))
                else:
                    if WITH_OCCLUDER:
                        torch.save(padded_locomotion, os.path.join(DATA_SAVE_DIR, "with_occluder", shape_type, scene_type, "{}.pth".format(n_restart)))
                    else:
                        torch.save(padded_locomotion, os.path.join(DATA_SAVE_DIR, "without_occluder", shape_type, scene_type, "{}.pth".format(n_restart)))

            env.controller.end_scene(None, None)






