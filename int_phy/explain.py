from shapely.geometry.polygon import Point, Polygon
import matplotlib.pyplot as plt


def get_pixel_polygon_from_state(state):
    p = state.edge_pixels
    object_bonding_pixels = [
        Point(p['x_min'], p['y_min']), Point(p['x_min'], p['y_max']),
        Point(p['x_max'], p['y_max']), Point(p['x_max'], p['y_min'])
    ]
    return Polygon(object_bonding_pixels)

def check_object_patially_occlusion(all_occluder_dict, object_state, all_object_dict, plot=False): # need to rewrite, use bonding box point
    occlusion = False
    if object_state.occluded_by or object_state.out_of_scene:
        occlusion = True
    else:
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

        for object_id, obj_state in all_object_dict.items():
            if object_state.id == obj_state.id:
                continue
            occluder_poly = get_pixel_polygon_from_state(obj_state)
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
