from int_phy.object_state import get_object_frame_info
from int_phy.object_state import get_bonding_box_polygon


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
    def __init__(self, object_info, depth_frame, object_frame):
        self.id = object_info.uuid
        self.color = object_info.color
        self.depth, self.edge_pixels = get_object_frame_info(object_info, depth_frame, object_frame, depth_aggregation=max)






