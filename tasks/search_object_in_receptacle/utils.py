import numpy as np
import ast
import matplotlib.pyplot as plt

def set_object_goal(faceTurner, scene_config):
    assert "goal" in scene_config
    if 'target' in scene_config['goal']['metadata']:
        target_object = scene_config['goal']['metadata']['target']
    elif 'target_1' in scene_config['goal']['metadata']:
        target_object = scene_config['goal']['metadata']['target_1']
    target_object_image = np.array(ast.literal_eval(target_object['image']))
    target_object_id = target_object['id']
    # plt.imshow(target_object_image)
    # plt.close()
    faceTurner.set_goal(target_object_image, target_object_id)










