import numpy as np


def project_to_2d(x, y, z, focal_length=30.85795):
    return x * focal_length / z, y * focal_length / z

def get_occluder_frame_info(object_info, depth_frame, object_frame):
    depth_frame = np.array(depth_frame)
    object_frame = np.array(object_frame)
    color = np.array([object_info.color['r'], object_info.color['g'], object_info.color['b']])
    pixel_match = (object_frame == color).sum(axis=-1)
    matched_pixels = [(x,y) for x,y in zip(*np.where(pixel_match == 3))]
    assert len(matched_pixels) > 0
    matched_pixels_x = [t[1] for t in matched_pixels]
    matched_pixels_y = [t[0] for t in matched_pixels]
    pixel_info = {
        'x_min': min(matched_pixels_x), 'x_max': max(matched_pixels_x),
        'y_min': min(matched_pixels_y), 'y_max': max(matched_pixels_y)
    }
    object_depth_frame_value = max([depth_frame[i,j] for i,j in matched_pixels])
    return object_depth_frame_value, pixel_info


def get_bonding_box_2d(bonding_box_3d, agent_position):
    vertices = []
    for vertex in bonding_box_3d:
        delta_x, delta_y, delta_z = None, None, None
        for k, v in vertex.items():
            if k == "x":
                delta_x = v - agent_position['x']
            elif k == "y":
                delta_y = v - agent_position['y']
            elif k == "z":
                delta_z = v - agent_position['z']
        assert delta_x and delta_y and delta_z
        x_2d, y_2d = project_to_2d(delta_x, delta_y, delta_z)
        vertices.append((round(x_2d), round(y_2d)))
    print(vertices)


def get_running_in_occluder_info(all_occluder_dicts, object_state):
    min_pixel_dis = float('inf')
    which_occluder = None
    closest_occuluder_dis = float('inf')
    if object_state.velocity[0] < 0:
        for occluder_name, occluder_state in all_occluder_dicts.items():
            occuluder_dis = abs(object_state.position[0] - occluder_state.position[0])
            if occuluder_dis >= 0 and occuluder_dis < closest_occuluder_dis:
                closest_occuluder_dis = occuluder_dis
                min_pixel_dis = object_state.edge_pixels['x_min'] - occluder_state.edge_pixels['x_max']
                which_occluder = occluder_name
    elif object_state.velocity[0] > 0:
        for occluder_name, occluder_state in all_occluder_dicts.items():
            occuluder_dis = abs(occluder_state.position[0] - object_state.position[0])
            if occuluder_dis >= 0 and occuluder_dis < closest_occuluder_dis:
                closest_occuluder_dis = occuluder_dis
                min_pixel_dis = occluder_state.edge_pixels['x_min'] - object_state.edge_pixels['x_max']
                which_occluder = occluder_name
    else:
        assert object_state.velocity[0] == 0 and object_state.velocity[1] < 0
        for occluder_name, occluder_state in all_occluder_dicts.items():
            occuluder_dis = abs(occluder_state.position[0] - object_state.position[0])
            if occuluder_dis < closest_occuluder_dis:
                closest_occuluder_dis = occuluder_dis
                min_pixel_dis = occluder_state.edge_pixels['y_min'] - object_state.edge_pixels['y_max']
                which_occluder = occluder_name
    return min_pixel_dis, which_occluder

def get_running_out_occluder_info(all_occluder_dicts, appear_state, estimate_state):
    min_pixel_dis = float('inf')
    which_occluder = None
    closest_occuluder_dis = float('inf')
    if estimate_state.velocity[0] < 0:
        for occluder_name, occluder_state in all_occluder_dicts.items():
            occuluder_dis = abs(occluder_state.position[0] - appear_state.position[0])
            if occuluder_dis >= 0 and occuluder_dis < closest_occuluder_dis:
                closest_occuluder_dis = occuluder_dis
                min_pixel_dis = occluder_state.edge_pixels['x_min'] - appear_state.edge_pixels['x_max']
                which_occluder = occluder_name
    elif estimate_state.velocity[0] > 0:
        for occluder_name, occluder_state in all_occluder_dicts.items():
            occuluder_dis = abs(appear_state.position[0] - occluder_state.position[0])
            if occuluder_dis >= 0 and occuluder_dis < closest_occuluder_dis:
                closest_occuluder_dis = occuluder_dis
                min_pixel_dis = appear_state.edge_pixels['x_min'] - occluder_state.edge_pixels['x_max']
                which_occluder = occluder_name
    else:
        assert estimate_state.velocity[0] == 0 and estimate_state.velocity[1] < 0
        for occluder_name, occluder_state in all_occluder_dicts.items():
            occuluder_dis = abs(occluder_state.position[0] - appear_state.position[0])
            if occuluder_dis < closest_occuluder_dis:
                closest_occuluder_dis = occuluder_dis
                min_pixel_dis = appear_state.edge_pixels['y_min'] - occluder_state.edge_pixels['y_max']
                which_occluder = occluder_name
    return min_pixel_dis, which_occluder



class OccluderState:
    def __init__(self, object_info, depth_frame, object_frame, agent_position):
        self.id = object_info.uuid
        self.color = object_info.color
        self.position = [object_info.position['x'], object_info.position['y'], object_info.position['z']]
        self.depth, self.edge_pixels = get_occluder_frame_info(object_info, depth_frame, object_frame)
        # print(min(self.edge_pixelss), max(self.edge_pixelss))
        # self.bonding_box = get_bonding_box_2d(object_info.dimensions, agent_position)






