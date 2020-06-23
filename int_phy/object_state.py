from copy import deepcopy
import numpy as np
import torch
from PIL import Image
from collections import defaultdict
from shapely.geometry import MultiPoint
from shapely.geometry.polygon import Polygon, Point


IMAGE_CROP_SIZE = 28



def get_object_match_pixels(object_color, object_frame):
    color = np.array([object_color['r'], object_color['g'], object_color['b']])
    pixel_match = (object_frame == color).sum(axis=-1)
    matched_pixels = [(x,y) for x,y in zip(*np.where(pixel_match == 3))]
    return matched_pixels


def get_object_frame_info(object_info, depth_frame, object_frame, depth_aggregation):
    depth_frame = np.array(depth_frame)
    object_frame = np.array(object_frame)
    matched_pixels = get_object_match_pixels(object_info.color, object_frame)
    assert len(matched_pixels) > 0
    matched_pixels_sorted_by_x = sorted(matched_pixels, key=lambda x: x[1])
    matched_pixels_sorted_by_y = sorted(matched_pixels, key=lambda x: x[0])
    pixel_info = {
        'x_min': matched_pixels_sorted_by_x[0][1], 'x_max': matched_pixels_sorted_by_x[-1][1],
        'y_min': matched_pixels_sorted_by_y[0][0], 'y_max': matched_pixels_sorted_by_y[-1][0],
        'x_min_y': matched_pixels_sorted_by_x[0][0], 'x_max_y': matched_pixels_sorted_by_x[-1][0],
        'y_min_x': matched_pixels_sorted_by_y[0][1], 'y_max_x': matched_pixels_sorted_by_y[-1][1]
    }
    object_depth_frame_value = depth_aggregation([depth_frame[i, j] for i, j in matched_pixels])
    return object_depth_frame_value, pixel_info

def pre_process_cropped_img(img):
    img = img.astype(np.float32)
    img /= 255
    img = torch.tensor(img).unsqueeze(0)
    return img


def get_cropped_object_appearane(object_frame, edge_pixels, obeject_color):
    object_frame = np.array(object_frame)
    x_s = edge_pixels['x_min']
    x_e = edge_pixels['x_max']
    y_s = edge_pixels['y_min']
    y_e = edge_pixels['y_max']
    new_size = (IMAGE_CROP_SIZE, IMAGE_CROP_SIZE)
    pixels_on_frame = get_object_match_pixels(obeject_color, object_frame)
    object_frame[:, :] = [255, 255, 255]
    for x, y in pixels_on_frame:
        object_frame[x, y, :] = [0, 0, 0]
    obj_frame = object_frame[y_s:y_e, x_s:x_e, :]
    obj_frame = Image.fromarray(obj_frame).convert('L').resize(new_size)
    obj_frame = pre_process_cropped_img(np.array(obj_frame)).unsqueeze(0)
    return obj_frame



def get_2d_bonding_box_point(dimensions):
    front_8_points = [dimensions[i] for i in range(8)]
    list_of_point_obj = []
    for p in front_8_points:
        list_of_point_obj.append( Point(p['x'], p['y']) )
    return list_of_point_obj

def get_bonding_box_polygon(object_info):
    bonding_box_point = get_2d_bonding_box_point(object_info.dimensions)
    return MultiPoint(bonding_box_point).convex_hull


class ObjectState:

    def __init__(self, object_info, depth_frame, object_frame):
        self.id = object_info.uuid
        self.color = object_info.color
        self.position = [object_info.position['x'], object_info.position['y'], object_info.position['z']]
        self.depth, self.edge_pixels = get_object_frame_info(object_info, depth_frame, object_frame, depth_aggregation=min)
        self.velocity = (0, 0)
        self.bonding_box_polygon = get_bonding_box_polygon(object_info)

        self.in_view = True
        self.occluded_by = None
        self.out_of_view = False

        self.appearance = None
        self.locomotion_feature = None
        self.appearance_cnt = defaultdict(lambda: 0)

    def in_view_update(self, new_object_state):
        v_x = round(new_object_state.position[0] - self.position[0], 3)
        v_y = round(new_object_state.position[1] - self.position[1], 3)
        v_z = round(new_object_state.position[2] - self.position[2], 3)

        self.velocity = [v_x, v_y]
        self.position = [new_object_state.position[0], new_object_state.position[1], new_object_state.position[2]]
        self.depth = new_object_state.depth
        self.edge_pixels = new_object_state.edge_pixels
        self.in_view = True


    def out_view_update(self, last_seen_state_and_occluders=None):
        if last_seen_state_and_occluders:
            last_seen_state, last_occluder = last_seen_state_and_occluders
            self.last_seen_state = deepcopy(last_seen_state)
            self.occluded_by = last_occluder


        self.edge_pixels = None
        self.in_view = False


    def appearance_update(self, decision, likelihood):
        # if self.appearance:
        #     old_decision, old_likelihood = self.appearance
        #     if old_decision != decision:
        #         print("object {} appearance change from {} to {}".format(self.id, old_decision, decision))
        #     else:
        #         print("object {} appearance dose not change".format(self.id))
        # else:
        #     print("object {} first appear as {}".format(self.id, decision))
        self.appearance = (decision, likelihood)
        self.appearance_cnt[decision] += 1


    def get_appearance_score(self):
        max_shape_cnt = 0
        total_cnt = 0
        print(self.appearance_cnt)
        for cnt in self.appearance_cnt.values():
            max_shape_cnt = max(cnt, max_shape_cnt)
            total_cnt += cnt
        return max_shape_cnt / total_cnt



