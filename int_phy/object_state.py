from copy import deepcopy
import numpy as np
import torch

IMAGE_CROP_SIZE = 56

def pre_process(img):
    img = img.astype(np.float32)
    img /= 255
    img = torch.tensor(img).unsqueeze(0)
    return img

def get_object_frame_info(object_info, depth_frame, object_frame):
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


def get_appearance(model, object_frame, pixels_on_frame):
    x_s = pixels_on_frame['x_min']
    x_e = pixels_on_frame['x_max']
    y_s = pixels_on_frame['y_min']
    y_e = pixels_on_frame['y_max']
    new_size = (IMAGE_CROP_SIZE, IMAGE_CROP_SIZE)
    obj_frame = np.array(object_frame.convert('L').crop((x_s, y_s, x_e, y_e)).resize(new_size))
    obj_frame = pre_process(obj_frame).unsqueeze(0)
    embedding = model(obj_frame)
    return embedding[0].detach()



class ObjectState:
    def __init__(self, object_info, depth_frame, object_frame, appearance_model):
        self.id = object_info.uuid
        self.position = [object_info.position['x'], object_info.position['y'], object_info.position['z']]
        self.depth, self.pixels_on_frame = get_object_frame_info(object_info, depth_frame, object_frame)
        self.velocity = (0, 0)
        self.in_view = True
        self.occluded_by = None
        self.out_of_view = False
        self.appearance = get_appearance(appearance_model, object_frame, self.pixels_on_frame)
        self.velocity_history = []

    def in_view_update(self, new_object_state):
        v_x = round(new_object_state.position[0] - self.position[0], 3)
        v_y = round(new_object_state.position[1] - self.position[1], 3)
        v_z = round(new_object_state.position[2] - self.position[2], 3)

        self.velocity = [v_x, v_y]
        self.position = [new_object_state.position[0], new_object_state.position[1], new_object_state.position[2]]
        self.depth = new_object_state.depth
        self.pixels_on_frame = new_object_state.pixels_on_frame
        self.in_view = True

        if v_z != 0:
            pass
            # print(v_z)
        if self.velocity is not None:
            self.velocity_history.append(self.velocity)

    def out_view_update(self, last_seen_state_and_occluders=None, constant_velocity=True):
        if last_seen_state_and_occluders:
            last_seen_state, last_occluder = last_seen_state_and_occluders
            self.last_seen_state = deepcopy(last_seen_state)
            self.occluded_by = last_occluder

        if constant_velocity:
            self.position[0] += self.velocity[0]
            self.position[1] += self.velocity[1]

        self.pixels_on_frame = None
        self.in_view = False

