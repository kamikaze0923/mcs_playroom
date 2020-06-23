from int_phy.occluder_state import get_running_in_occluder_info, get_running_out_occluder_info
from shapely.geometry.polygon import Point, Polygon
import matplotlib.pyplot as plt


EDGE_MARGIN = 50


def explain_for_disappearance_by_out_of_scene(pre_state, frame_size):
    explain_success = False
    if frame_size[0] - pre_state.edge_pixels['x_max'] <= EDGE_MARGIN:
        assert pre_state.velocity[0] > 0
        print("object {} come out of scene from right edge".format(pre_state.id))
        explain_success = True
    elif pre_state.edge_pixels['x_min'] <= EDGE_MARGIN:
        assert pre_state.velocity[0] < 0
        print("object {} come out of scene from left edge".format(pre_state.id))
        explain_success = True
    return explain_success


def explain_for_re_appearance(appear_state, estimate_state, new_occluder_state_dict):
    explain_success = False
    distance_to_occluder, occluder_name = get_running_out_occluder_info(new_occluder_state_dict, appear_state, estimate_state)
    if distance_to_occluder <= EDGE_MARGIN:
        print("object {} run out of {}".format(appear_state.id, occluder_name))
        explain_success = occluder_name
    return explain_success


def explain_for_disappearance_by_occlusion(pre_state, new_occluder_state_dict):
    explain_success = False
    distance_to_occluder, occluder_name = get_running_in_occluder_info(new_occluder_state_dict, pre_state)
    if distance_to_occluder <= EDGE_MARGIN:
        explain_success = occluder_name
        print("object {} run into {}".format(pre_state.id, occluder_name))
    return explain_success


def get_pixel_polygon_from_state(state):
    p = state.edge_pixels
    object_bonding_pixels = [
        Point(p['x_min'], p['y_min']), Point(p['x_min'], p['y_max']),
        Point(p['x_max'], p['y_max']), Point(p['x_max'], p['y_min'])
    ]
    return Polygon(object_bonding_pixels)



def check_object_patially_occlusion(all_occluder_dict, object_state, plot=False): # need to rewrite, use bonding box point
    occlusion = False
    # for occluder_id, occluder_state in all_occluder_dict.items():
    #     if object_state.bonding_box_polygon.intersects(occluder_state.bonding_box_polygon):
    #         occlusion = True
    #         # print("{} occlude {}".format(occluder_id, object_state.id))
    #     if plot:
    #         plt.cla()
    #         plt.axis('equal')
    #         new_shape = so.cascaded_union([object_state.bonding_box_polygon, occluder_state.bonding_box_polygon])
    #         for geom in new_shape.geoms:
    #             xs, ys = geom.exterior.xy
    #             plt.fill(xs, ys, alpha=0.5, fc='r', ec='none')
    #         plt.pause(0.2)

    obj_poly = get_pixel_polygon_from_state(object_state)

    if plot:
        plt.cla()
        plt.axis('equal')
        x, y = obj_poly.exterior.xy
        plt.plot(x,y, color='r')
    for occluder_id, occluder_state in all_occluder_dict.items():
        occluder_poly = get_pixel_polygon_from_state(occluder_state)
        if plot:
            x, y = occluder_poly.exterior.xy
            plt.plot(x, y, color='b')
            plt.pause(0.1)
        dis = obj_poly.distance(occluder_poly)
        if dis <= 1:
            occlusion = True


    return occlusion

def check_object_on_edge(object_state, frame_size):
    occlusion = False
    if object_state.edge_pixels['x_min'] == 0:
        occlusion = True
        # print("Object {} on left edge".format(object_state.id))
    if object_state.edge_pixels['y_min'] == 0:
        occlusion = True
        # print("Object {} on top edge".format(object_state.id))
    if object_state.edge_pixels['x_max'] == frame_size[0] - 1:
        occlusion = True
        # print("Object {} on right edge".format(object_state.id))
    return occlusion


