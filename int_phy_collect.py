from gym_ai2thor.envs.mcs_env import McsEnv
from int_phy.object_state import ObjectState, pre_process, IMAGE_CROP_SIZE
import numpy as np
import torch
import os

def set_scale(config, scale):
    config['objects'][0]['shows'][0]['scale']['x'] = scale
    config['objects'][0]['shows'][0]['scale']['y'] = scale
    config['objects'][0]['shows'][0]['scale']['z'] = scale


if __name__ == "__main__":
    shape_types = ["sphere", "cube"]
    scene_name = "github_scenes" + "/collect_object_shape_data"
    start_scene_number = 1
    print("Scene: {}".format(start_scene_number))
    env = McsEnv(task="intphys_scenes", scene_type=scene_name, start_scene_number=start_scene_number)
    env.reset(random_init=False)

    object_frames = []
    for scale in [0.3 + 0.1*i for i in range(10)]:
        set_scale(env.scene_config, scale)
        env.step_output = env.controller.start_scene(env.scene_config)
        for i, x in enumerate(env.scene_config['goal']['action_list']):
            env.step(action=x[0])
            assert len(env.step_output.object_list) <= 1
            if len(env.step_output.object_list) == 1:
                obj_state = ObjectState(
                    env.step_output.object_list[0], env.step_output.depth_mask_list[-1], env.step_output.object_mask_list[-1]
                )
                x_s = obj_state.pixels_on_frame['x_min']
                x_e = obj_state.pixels_on_frame['x_max']
                y_s = obj_state.pixels_on_frame['y_min']
                y_e = obj_state.pixels_on_frame['y_max']
                new_size = (IMAGE_CROP_SIZE, IMAGE_CROP_SIZE)
                obj_frame = env.step_output.object_mask_list[-1].convert('L').crop((x_s, y_s, x_e, y_e)).resize(new_size)
                if i >= 3 and i < 3 + 12:
                    obj_frame.show()
                    obj_frame = np.array(obj_frame)
                    object_frames.append(pre_process(obj_frame))

    env.controller.end_scene(None, None)
    object_frames = torch.stack(object_frames)
    print(object_frames.size())
    torch.save(object_frames, os.path.join("object_mask_frame", shape_types[start_scene_number], "0.pth"))

