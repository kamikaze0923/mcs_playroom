import numpy as np
import torch
from PIL import Image
from collections import defaultdict
from shapely.geometry import MultiPoint
from shapely.geometry.polygon import Point, Polygon
from int_phy.locomotion.network import HIDDEN_STATE_SIZE, NUM_HIDDEN_LAYER, POSITION_FEATURE_DIM


IMAGE_CROP_SIZE = 28
ON_GROUND_THRESHOLD = 1e-1

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

def get_support_indicator(step_output, obj_bonding_p):
    grounds = list(filter(lambda x: "floor" in x.uuid, step_output.structural_object_list))
    assert len(grounds) == 1
    ramps = list(filter(lambda x: "ramp" in x.uuid, step_output.structural_object_list))
    support_objs = grounds + ramps
    indicator = [0]
    support_dis = float('inf')
    for obj in support_objs:
        polygon = get_bonding_box_polygon(obj)
        for p in obj_bonding_p:
            if polygon.distance(p) < ON_GROUND_THRESHOLD:
                indicator = [1]
                support_dis = polygon.distance(p)
                break
        if indicator[0] == 1:
            break
    # print(indicator, support_dis)
    return indicator

def get_locomotion_feature(step_output, object_occluded, object_in_scene, obj_info):
    if step_output is None:
        obj = None
    else:
        obj = obj_info
    features = []
    if not object_in_scene:
        features.extend([0.0] * 27) # position + bonding_box
        # features.extend([0.0]) # supported
        features.extend([0.0, 0.0])# occluded, in_scene
    else:
        if object_occluded:
            features.extend([0.0] * 27)
            # features.extend([0.0])  # supported
            features.extend([0.0, 1.0])
        else:
            features.append(obj.position['x'])
            features.append(obj.position['y'])
            features.append(obj.position['z'])
            bonding_xy = []
            for bonding_vertex in obj.dimensions:
                features.append(bonding_vertex['x'])
                features.append(bonding_vertex['y'])
                bonding_xy.append(Point(bonding_vertex['x'], bonding_vertex['y']))
                features.append(bonding_vertex['z'])
            # step_output.object_mask_list[-1].show()
            # features.extend(get_support_indicator(step_output, bonding_xy))
            features.extend([1.0, 1.0])

    assert len(features) == POSITION_FEATURE_DIM
    return torch.tensor(features)


class ObjectState:

    def __init__(self, object_info, depth_frame, object_frame, step_output):
        self.id = object_info.uuid
        self.color = object_info.color
        self.loc_f = get_locomotion_feature(step_output, False, True, object_info).unsqueeze(0).unsqueeze(0)
        self.h_t = torch.zeros(size=(NUM_HIDDEN_LAYER, 1, HIDDEN_STATE_SIZE))
        self.c_t = torch.zeros(size=(NUM_HIDDEN_LAYER, 1, HIDDEN_STATE_SIZE))
        self.depth, self.edge_pixels = get_object_frame_info(object_info, depth_frame, object_frame, depth_aggregation=min)

        self.appearance = None
        self.locomotion_feature = None
        self.appearance_cnt = defaultdict(lambda: 0)

        self.next_step_position = None
        self.next_step_leave_scene_prob = None

    def in_view_update(self, new_object_state, locomotion_checker):
        self.loc_f = new_object_state.loc_f
        next_info, next_hidden = locomotion_checker.predict(self.loc_f, self.h_t, self.c_t)
        self.next_step_position, self.next_step_leave_scene_prob = next_info
        self.h_t, self.c_t = next_hidden
        a = 1


    def out_view_update(self, locomotion_checker):
        pass



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
        # print(self.appearance_cnt)
        for cnt in self.appearance_cnt.values():
            max_shape_cnt = max(cnt, max_shape_cnt)
            total_cnt += cnt
        return max_shape_cnt / total_cnt



