from gym_ai2thor.envs.mcs_env import McsEnv
from int_phy.object_state import ObjectState, pre_process_cropped_img, IMAGE_CROP_SIZE, get_object_match_pixels
from PIL import Image
import numpy as np
import torch
import os

SHAPE_TYPES = ["cylinder", "sphere", "cube"]
all_scene = ["object_permanence", "shape_constancy", "spatio_temporal_continuity"]


def get_locomotion_feature(obj):
    features = []
    features.append(obj.position['x'])
    features.append(obj.position['y'])
    features.append(obj.position['z'])
    for bonding_vertex in obj.dimensions:
        features.append(bonding_vertex['x'])
        features.append(bonding_vertex['y'])
        features.append(bonding_vertex['z'])
    features.append(1)
    return torch.tensor(features)


if __name__ == "__main__":
    scene_name = "github_scenes" + "/collect_object_shape_data"

    object_frames = {}
    object_locomotions = {}
    for _, shape_type in enumerate(SHAPE_TYPES):
        os.makedirs(os.path.join("appearance", "object_mask_frame", shape_type), exist_ok=True)
        os.makedirs(os.path.join("appearance", "locomotion", shape_type), exist_ok=True)
        object_frames[shape_type] = []
        object_locomotions[shape_type] = []

    for scene_name in all_scene:
        env = McsEnv(task="intphys_scenes", scene_type=scene_name)
        while env.current_scene < len(env.all_scenes) - 1078:
            env.reset(random_init=False)
            env_new_objects = []
            for obj in env.scene_config['objects']:
                if "occluder" not in obj['id']:
                    env_new_objects.append(obj)
            for one_obj in env_new_objects:
                env.scene_config['objects']  = [one_obj]
                env.step_output = env.controller.start_scene(env.scene_config)
                obj_in = False
                one_episode_locomotion = []
                for i, action in enumerate(env.scene_config['goal']['action_list']):
                    env.step(action=action[0])
                    if len(env.step_output.object_list) == 1:
                        obj_in = True
                        obj_state = ObjectState(
                            env.step_output.object_list[0], env.step_output.depth_mask_list[-1], env.step_output.object_mask_list[-1]
                        )
                        x_s = obj_state.edge_pixels['x_min']
                        x_e = obj_state.edge_pixels['x_max']
                        y_s = obj_state.edge_pixels['y_min']
                        y_e = obj_state.edge_pixels['y_max']
                        if x_s == 0 or y_s == 0 or x_e == env.step_output.camera_aspect_ratio[0] - 1 or x_e == env.step_output.camera_aspect_ratio[1] - 1:
                            continue
                        new_size = (IMAGE_CROP_SIZE, IMAGE_CROP_SIZE)
                        obj_frame = np.array(env.step_output.object_mask_list[-1])
                        pixels_on_frame = get_object_match_pixels(env.step_output.object_list[0].color, obj_frame)
                        obj_frame[:,:] = [255, 255, 255]
                        for x,y in pixels_on_frame:
                            obj_frame[x,y,:] = [0, 0, 0]
                        obj_frame = obj_frame[y_s:y_e, x_s:x_e, :]
                        obj_frame = Image.fromarray(obj_frame).convert('L').resize(new_size)
                        # obj_frame.show()
                        obj_frame = np.array(obj_frame)
                        object_frames[one_obj['type']].append(pre_process_cropped_img(obj_frame))
                        one_episode_locomotion.append(get_locomotion_feature(env.step_output.object_list[0]))
                    if obj_in and len(env.step_output.object_list) == 0:
                        break
                object_locomotions[one_obj['type']].append(torch.stack(one_episode_locomotion))
        env.controller.end_scene(None, None)

    for _, shape_type in enumerate(SHAPE_TYPES):
        one_type_frames = object_frames[shape_type]
        one_type_frames = torch.stack(one_type_frames)
        print(one_type_frames.size())
        torch.save(one_type_frames, os.path.join("appearance", "object_mask_frame", shape_type, "0.pth"))

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
        torch.save(one_type_frames, os.path.join("appearance", "locomotion", shape_type, "0.pth"))




