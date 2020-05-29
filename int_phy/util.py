import numpy as np

def get_occluder_pixels(object_depth, depth_frame, object_frame):
    occluder_pixels_with_ground = [(x, y) for x, y in zip(*np.where(depth_frame < object_depth))]
    ground_pixel = object_frame[299,299]
    occluder_pixels = [(x,y) for x,y in occluder_pixels_with_ground if np.not_equal(object_frame[x,y], ground_pixel).any()]
    return occluder_pixels


def get_object_frame_info(object_info, depth_frame, object_frame):
    depth_frame = np.array(depth_frame)
    object_frame = np.array(object_frame)
    color = np.array([object_info.color['r'], object_info.color['g'], object_info.color['b']])
    pixel_match = (object_frame == color).sum(axis=-1)
    matched_pixels = [(x,y) for x,y in zip(*np.where(pixel_match == 3))]
    assert len(matched_pixels) > 0
    object_depth_frame_value = [depth_frame[i,j] for i,j in matched_pixels]
    return min(object_depth_frame_value), matched_pixels


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


