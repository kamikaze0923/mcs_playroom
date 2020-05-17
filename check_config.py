import os
import machine_common_sense
import ast
import numpy as np
import matplotlib.pyplot as plt
from skimage import transform

interaction_sceces = "transferral"

goal_dir = os.path.join("interaction_scenes", interaction_sceces)
all_scenes = sorted(os.listdir(goal_dir))
all_scenes = [os.path.join(goal_dir, one_scene) for one_scene in all_scenes]
current_scene = -1

object_set = set()

while current_scene < len(all_scenes) - 1:
    current_scene += 1
    scene_config, _ = machine_common_sense.MCS.load_config_json_file(all_scenes[current_scene])

    assert "goal" in scene_config
    if 'target' in scene_config['goal']['metadata']:
        target_object = scene_config['goal']['metadata']['target']
    elif 'target_2' in scene_config['goal']['metadata']:
        target_object = scene_config['goal']['metadata']['target_2']
    assert 'target_2' in scene_config['goal']['metadata']
    if scene_config['goal']['metadata']['relationship'][1] == "on top of":
        obj_name = scene_config['goal']['metadata']['target_2']['image_name'].split("_", maxsplit=2)
        obj_name = "_".join(obj_name[:2])
        object_set.add(obj_name)
    # target_object_image = np.array(ast.literal_eval(target_object['image']))
    # target_object_image = target_object_image.astype(np.float64) / 255
    # img = transform.resize(target_object_image, (64, 64, 3)) * 255
    # img = img.astype(np.uint8)
    # plt.imshow(img)
    # print(target_object_image.shape)

for i in sorted(list(object_set)):
    print(i)
