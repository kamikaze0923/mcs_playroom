import numpy as np
import torch
from PIL import Image
from collections import defaultdict
from shapely.geometry import MultiPoint
from shapely.geometry.polygon import Point
from int_phy.locomotion.network import HIDDEN_STATE_SIZE, NUM_HIDDEN_LAYER, POSITION_FEATURE_DIM
import matplotlib.pyplot as plt


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
    # assert len(matched_pixels) > 0
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

    def __init__(self, object_info, depth_frame, object_frame, step_output, plot):
        self.id = object_info.uuid
        self.color = object_info.color
        self.loc_f = get_locomotion_feature(step_output, False, True, object_info).unsqueeze(0).unsqueeze(0)
        self.h_t = torch.zeros(size=(NUM_HIDDEN_LAYER, 1, HIDDEN_STATE_SIZE))
        self.c_t = torch.zeros(size=(NUM_HIDDEN_LAYER, 1, HIDDEN_STATE_SIZE))
        self.depth, self.edge_pixels = get_object_frame_info(object_info, depth_frame, object_frame, depth_aggregation=min)

        self.appearance = None
        self.locomotion_feature = None
        self.appearance_cnt = defaultdict(lambda: 0)
        self.dir = self.get_horizontal_moveing_dir(object_info, step_output)

        self.next_step_position = None
        self.next_step_leave_scene_prob = None
        self.locomotion_cnt = {"near": 0, "far": 0}

        self.occluded_by = None
        self.out_of_scene = False

        self.plot = plot

    def get_horizontal_moveing_dir(self, object_info, step_output, epsl=5):
        dir = None
        try:
            _, edge_pixel_prev = get_object_frame_info(
                object_info, step_output.depth_mask_list[-2], step_output.object_mask_list[-2], depth_aggregation=min
            )
            _, edge_pixel_now = get_object_frame_info(
                object_info, step_output.depth_mask_list[-1], step_output.object_mask_list[-1], depth_aggregation=min
            )
            if edge_pixel_prev['x_max'] - edge_pixel_now['x_max'] > epsl or edge_pixel_prev['x_min'] - edge_pixel_now['x_min'] > epsl:
                dir = 'left'
            if edge_pixel_now['x_max'] - edge_pixel_prev['x_max'] > epsl or edge_pixel_now['x_min'] - edge_pixel_prev['x_min'] > epsl:
                dir = 'right'
        except:
            pass
        return dir

    def loc_update(self, locomotion_checker):
        next_info, next_hidden = locomotion_checker.predict(self.loc_f, self.h_t, self.c_t)
        self.next_step_position = next_info[0].squeeze().detach().cpu().numpy()
        self.next_step_leave_scene_prob = next_info[1].squeeze().detach().cpu().numpy()
        self.h_t, self.c_t = next_hidden

    def loc_in_view_update(self, new_object_state, locomotion_checker):
        if self.next_step_position is not None:
            self.error_update_in_view(new_object_state, locomotion_checker)
        else:
            BOTTOM_BONDING_BOX_INDEX = [4,7,10,13]
            ON_GROUND_THRESHOLD = 0.1
            CENTER_X = 2

            if min(new_object_state.loc_f[0][0][BOTTOM_BONDING_BOX_INDEX]) < ON_GROUND_THRESHOLD:
                if new_object_state.dir is None:
                    if abs(new_object_state.loc_f[0][0][0]) < CENTER_X:
                        self.locomotion_cnt['far'] += 1
                        # print("Object Suddenly Appear")
                elif new_object_state.dir == "left":
                    if new_object_state.loc_f[0][0][0] > 0:
                        self.locomotion_cnt['far'] += 1
                        # print("Object Suddenly Appear")
                elif new_object_state.dir == "right":
                    if new_object_state.loc_f[0][0][0] < 0:
                        self.locomotion_cnt['far'] += 1
                        # print("Object Suddenly Appear")


            if self.plot:
                ground_truth = new_object_state.loc_f.squeeze()[:2].detach().cpu().numpy()
                plt.plot(ground_truth[0], ground_truth[1], color='r', marker='x')
                plt.pause(0.1)

        self.occluded_by = None
        self.loc_f = new_object_state.loc_f
        self.edge_pixels = new_object_state.edge_pixels
        self.depth = new_object_state.depth
        self.loc_update(locomotion_checker)

    def loc_out_view_update(self, new_occluder_state_dict, locomotion_checker):
        non_seen_f = get_locomotion_feature(None, True, True, None).unsqueeze(0).unsqueeze(0)
        self.loc_f = non_seen_f
        self.edge_pixels = None
        self.depth = None
        self.loc_update(locomotion_checker)
        if self.next_step_position is not None and self.next_step_leave_scene_prob is not None:
            if self.next_step_leave_scene_prob > locomotion_checker.LEAVE_SCENE_PROB_TRESHOLD and not self.out_of_scene:
                self.out_of_scene = True
                # print("Predicting Object has left the scene with probability {:.4f}".format(self.next_step_leave_scene_prob))
            else:
                if not self.out_of_scene:
                    # print("Predicting Object has been occluded, probability of it leave the scene {:.4f}".format(self.next_step_leave_scene_prob))
                    self.error_update_out_view(new_occluder_state_dict, locomotion_checker)


    def error_update_in_view(self, new_object_state, locomotion_checker):
        if not self.out_of_scene:
            ground_truth = new_object_state.loc_f.squeeze()[:2].detach().cpu().numpy()
            error = np.sum(np.square(ground_truth - self.next_step_position))
            threshold = locomotion_checker.LOCOMOTION_MSE_ERROR_THRESHOLD
            if self.occluded_by is not None:
                threshold = locomotion_checker.LOCOMOTION_MSE_ERROR_THRESHOLD_UNSEEN
            if error > threshold:
                self.locomotion_cnt['far'] += 1
                # print("Unreasonable with error {:.4f}".format(error))
            else:
                self.locomotion_cnt['near'] += 1
                # print("Reasonable with error {:.4f}".format(error))
            if self.plot:
                plt.plot(self.next_step_position[0], self.next_step_position[1], color='b', marker='x')
                plt.pause(0.1)
                plt.plot(ground_truth[0], ground_truth[1], color='r', marker='x')
                plt.pause(0.1)

        else:
            print("Predicted Object {} out of scene but re-appears".format(new_object_state.id))
            self.locomotion_cnt['far'] += 1


    def error_update_out_view(self, new_occluder_state_dict, locomotion_checker):
        if not self.out_of_scene:
            pred_occluded_by = None
            for id, occluder_state in new_occluder_state_dict.items():
                if occluder_state.bonding_box_poly.contains(Point(self.next_step_position)):
                    pred_occluded_by = id
                    self.locomotion_cnt['near'] += 1
                    # print("Reasonable with error 0")

            if not pred_occluded_by:
                if self.occluded_by:
                    threshold = locomotion_checker.LOCOMOTION_MSE_ERROR_THRESHOLD_UNSEEN
                    poly = new_occluder_state_dict[self.occluded_by].bonding_box_poly
                    error = np.square(poly.distance(Point(self.next_step_position)))
                    if error > threshold:
                        self.locomotion_cnt['far'] += 1
                        # print("Unreasonable with error {:.4f}".format(error))
                    else:
                        self.locomotion_cnt['near'] += 1
                        # print("Reasonable with error {:.4f}".format(error))

                    if self.plot:
                        plt.plot(self.next_step_position[0], self.next_step_position[1], color='b', marker='x')
                        plt.pause(0.1)
                        x, y = poly.exterior.xy
                        plt.plot(x, y, 'k')
                        plt.pause(0.1)
                else:
                    min_error = float('inf')
                    min_error_poly = None
                    for id, occluder_state in new_occluder_state_dict.items():
                        poly = occluder_state.bonding_box_poly
                        error = np.square(poly.distance(Point(self.next_step_position)))
                        if error < min_error:
                            self.occluded_by = id
                            min_error = error
                            min_error_poly = poly
                    if min_error > locomotion_checker.LOCOMOTION_MSE_ERROR_THRESHOLD:
                        self.locomotion_cnt['far'] += 1
                        # print("Unreasonable with error {:.4f}".format(error))
                    else:
                        self.locomotion_cnt['near'] += 1
                            # print("Reasonable with error {:.4f}".format(error))

                    if self.plot:
                        plt.plot(self.next_step_position[0], self.next_step_position[1], color='b', marker='x')
                        plt.pause(0.1)
                        x, y = min_error_poly.exterior.xy
                        plt.plot(x, y, 'k')
                        plt.pause(0.1)
            else:
                self.occluded_by = pred_occluded_by
                if self.plot:
                    plt.plot(self.next_step_position[0], self.next_step_position[1], color='b', marker='x')
                    plt.pause(0.1)
                    x, y = new_occluder_state_dict[self.occluded_by].bonding_box_poly.exterior.xy
                    plt.plot(x, y, 'k')
                    plt.pause(0.1)


    def get_locomotion_score(self):
        # print(self.locomotion_cnt)
        return 0.0 if self.locomotion_cnt['far'] > 0 else 1.0


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
        return 1.0 if total_cnt == 0 else max_shape_cnt / total_cnt



