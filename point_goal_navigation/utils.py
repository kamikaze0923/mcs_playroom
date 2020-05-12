import numpy as np
import quaternion
import random


def normalize_3d_rotation(delta_x, delta_y, delta_z):
    if delta_x == 0 and delta_y == 0 and delta_z ==0:
        return 0, 0, 0
    norm = (delta_x ** 2 + delta_y ** 2 + delta_z ** 2) ** 0.5
    return delta_x / norm, delta_y / norm, delta_z / norm

def quaternion_rotate_vector(quat, v):
    vq = np.quaternion(0, 0, 0, 0)
    vq.imag = v
    return (quat * vq * quat.inverse()).imag

def quat_from_angle_axis(theta, axis=np.array([0,1,0])):
    axis = axis.astype(np.float)
    axis /= np.linalg.norm(axis)
    return quaternion.from_rotation_vector(theta * axis)

def set_random_object_goal(navigator, scene_config):
    assert "objects" in scene_config
    assert "goal" in scene_config
    if scene_config['goal']['category'] == 'retrieval':
        target_object_id = scene_config['goal']['metadata']['target']['id']
    obj_info = list(filter(lambda l: l['id'] == target_object_id, scene_config['objects']))
    assert len(obj_info) == 1
    obj_info = obj_info[0]
    obj_position_info = obj_info['shows'][0]['position']
    navigator.goal = (obj_position_info['x'], obj_position_info['y'], obj_position_info['z'])









