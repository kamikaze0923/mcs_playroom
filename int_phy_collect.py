from gym_ai2thor.envs.mcs_env import McsEnv
from int_phy.object_state import ObjectState, pre_process_cropped_img, IMAGE_CROP_SIZE, get_object_match_pixels
from PIL import Image
import numpy as np
import torch
import os

SHAPE_TYPES = ["cylinder", "sphere", "cube"]

def set_scale(config, scale):
    config['objects'][0]['shows'][0]['scale']['x'] = scale
    config['objects'][0]['shows'][0]['scale']['y'] = scale
    config['objects'][0]['shows'][0]['scale']['z'] = scale


if __name__ == "__main__":
    scene_name = "github_scenes" + "/collect_object_shape_data"

    for _, shape_type in enumerate(SHAPE_TYPES):
        print("Scene: {}".format(shape_type))
        os.makedirs(os.path.join("appearance", "object_mask_frame", shape_type), exist_ok=True)
        env = McsEnv(task="intphys_scenes", scene_type=scene_name)
        env.reset(random_init=False)
        env.scene_config['objects'][0]['type'] = shape_type
        env.step_output = env.controller.start_scene(env.scene_config)

        object_frames = []
        for scale in [0.2 + 0.1*i for i in range(10)]:
            set_scale(env.scene_config, scale)
            env.step_output = env.controller.start_scene(env.scene_config)
            for i, action in enumerate(env.scene_config['goal']['action_list']):
                env.step(action=action[0])
                assert len(env.step_output.object_list) <= 1
                if len(env.step_output.object_list) == 1:
                    obj_state = ObjectState(
                        env.step_output.object_list[0], env.step_output.depth_mask_list[-1], env.step_output.object_mask_list[-1]
                    )
                    x_s = obj_state.edge_pixels['x_min']
                    x_e = obj_state.edge_pixels['x_max']
                    y_s = obj_state.edge_pixels['y_min']
                    y_e = obj_state.edge_pixels['y_max']
                    new_size = (IMAGE_CROP_SIZE, IMAGE_CROP_SIZE)
                    obj_frame = np.array(env.step_output.object_mask_list[-1])
                    pixels_on_frame = get_object_match_pixels(env.step_output.object_list[0].color, obj_frame)
                    obj_frame[:,:] = [255, 255, 255]
                    for x,y in pixels_on_frame:
                        obj_frame[x,y,:] = [0, 0, 0]
                    obj_frame = obj_frame[y_s:y_e, x_s:x_e, :]
                    obj_frame = Image.fromarray(obj_frame).convert('L').resize(new_size)
                    if i >= 3 and i < 3 + 12:
                        # obj_frame.show()
                        obj_frame = np.array(obj_frame)
                        object_frames.append(pre_process_cropped_img(obj_frame))

        env.controller.end_scene(None, None)
        object_frames = torch.stack(object_frames)
        print(object_frames.size())
        torch.save(object_frames, os.path.join("appearance", "object_mask_frame", shape_type, "0.pth"))
        env.controller.end_scene(None, None)

