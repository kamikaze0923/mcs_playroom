from copy import deepcopy
import numpy as np
import torch
from PIL import Image
from int_phy_recollect_position import get_locomotion_feature


IMAGE_CROP_SIZE = 28

def pre_process_cropped_img(img):
    img = img.astype(np.float32)
    img /= 255
    img = torch.tensor(img).unsqueeze(0)
    return img


def get_object_match_pixels(object_color, object_frame):
    color = np.array([object_color['r'], object_color['g'], object_color['b']])
    pixel_match = (object_frame == color).sum(axis=-1)
    matched_pixels = [(x,y) for x,y in zip(*np.where(pixel_match == 3))]
    return matched_pixels


def get_object_frame_info(object_info, depth_frame, object_frame):
    depth_frame = np.array(depth_frame)
    object_frame = np.array(object_frame)
    matched_pixels = get_object_match_pixels(object_info.color, object_frame)
    assert len(matched_pixels) > 0
    matched_pixels_x = [t[1] for t in matched_pixels]
    matched_pixels_y = [t[0] for t in matched_pixels]
    pixel_info = {
        'x_min': min(matched_pixels_x), 'x_max': max(matched_pixels_x),
        'y_min': min(matched_pixels_y), 'y_max': max(matched_pixels_y)
    }
    object_depth_frame_value = min([depth_frame[i,j] for i,j in matched_pixels])
    return object_depth_frame_value, pixel_info


def get_object_dimension(dimensions):
    arr = []
    for row in dimensions:
        arr.append([round(row['x'], 2), round(row['y'], 2), round(row['z'], 2)])
    arr = np.stack(arr)
    distance_matrix = np.zeros(shape=(arr.shape[0], arr.shape[0]))
    for i,x in enumerate(arr):
        for j,y in enumerate(arr):
            if j <= i:
                distance_matrix[i, j] = np.sqrt(np.sum(np.square(x - y)))
    return distance_matrix

def get_object_mask_color(color):
    return (color['r'], color['g'], color['b'])


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



class ObjectState:

    def __init__(self, object_info, depth_frame, object_frame):
        self.id = object_info.uuid
        self.color = object_info.color
        self.position = [object_info.position['x'], object_info.position['y'], object_info.position['z']]
        self.depth, self.edge_pixels = get_object_frame_info(object_info, depth_frame, object_frame)
        self.velocity = (0, 0)

        self.in_view = True
        self.occluded_by = None
        self.out_of_view = False

        self.appearance = None
        self.locomotion_feature = None

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
        if self.appearance:
            old_decision, old_likelihood = self.appearance
            if old_decision != decision:
                print("object {} appearance change from {} to {}".format(self.id, old_decision, decision))
                exit(0)
            else:
                print("object {} appearance dose not change".format(self.id))
        else:
            print("object {} first appear as {}".format(self.id, decision))
        self.appearance = (decision, likelihood)



