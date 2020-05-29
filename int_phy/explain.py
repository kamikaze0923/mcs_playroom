from int_phy.util import *
import numpy as np


EDGE_MARGIN = 50

def explain_for_first_appearance(state, frame_size):
    explain_success = False
    x_pixels = [pixel[1] for pixel in state.pixels_on_frame]
    y_pixels = [pixel[0] for pixel in state.pixels_on_frame]
    if frame_size[0] - max(x_pixels) <= EDGE_MARGIN:
        print("Object {} come from right into scene".format(state.id))
        explain_success = True
    elif min(x_pixels) <= EDGE_MARGIN:
        print("Object {} come from left into scene".format(state.id))
        explain_success = True
    if min(y_pixels) <= EDGE_MARGIN:
        print("Object {} come from top into scene".format(state.id))
        explain_success = True
    return explain_success


def explain_for_re_appearance(appear_state, dis_appear_state, new_depth_frame, new_object_frame):
    explain_success = False
    appear_state.is_occluded = False
    new_depth_frame = np.array(new_depth_frame)
    new_object_frame = np.array(new_object_frame)
    occluder_pixels = get_occluder_pixels(appear_state.depth, new_depth_frame, new_object_frame)
    # occluder_depth_frame_value = [new_depth_frame[i, j] for i, j in occluder_pixels]
    if dis_appear_state.velocity[0] < 0:
        right_most_object_pixel = max([x[1] for x in appear_state.pixels_on_frame])
        left_occluder_pixels = [x for x in occluder_pixels if x[1] > right_most_object_pixel]
        dis_to_occluder = min([(x[1] - right_most_object_pixel) for x in left_occluder_pixels])
        print("Object {} run out of occluder from left".format(appear_state.id))
        explain_success = True
    elif dis_appear_state.velocity[0] > 0:
        left_most_object_pixel = min([x[1] for x in appear_state.pixels_on_frame])
        right_occluder_pixels = [x for x in occluder_pixels if x[1] < left_most_object_pixel]
        dis_to_occluder = min([(left_most_object_pixel - x[1]) for x in right_occluder_pixels])
        explain_success = True
        print("Object {} run out of occluder from right".format(appear_state.id))
    elif dis_appear_state.velocity[0] == 0 and dis_appear_state.velocity[1] < 0:
        last_depth_frame = np.array(dis_appear_state.last_depth_frame)
        last_object_frame = np.array(dis_appear_state.last_object_frame)
        last_occluder_pixels = get_occluder_pixels(dis_appear_state.depth, last_depth_frame, last_object_frame)
        last_occluder_pixels_bottom = max([x[0] for x in last_occluder_pixels])
        occluder_pixels_bottom = max([x[0] for x in occluder_pixels])
        if last_occluder_pixels_bottom > occluder_pixels_bottom:
            explain_success = True
            print("Object {} run out of occluder because occluder is lifted up".format(appear_state.id))
    diff = np.square(dis_appear_state.shape - appear_state.shape)
    diff = np.sum(diff)
    print("Diff: {}".format(diff))
    if diff > 0.01:
        explain_success = False
        print("Object {} shape changes".format(appear_state.id))
    return explain_success

def explain_for_disappearance_by_out_of_scene(pre_state, frame_size):
    explain_success = False
    x_pixels = [pixel[1] for pixel in pre_state.pixels_on_frame]
    if abs(max(x_pixels) - frame_size[0]) <= EDGE_MARGIN:
        if pre_state.velocity[0] > 0:
            print("Object {} come out of scene from right edge".format(pre_state.id))
            explain_success = True
    elif abs(min(x_pixels)) <= EDGE_MARGIN:
        if pre_state.velocity[0] < 0:
            print("Object {} come out of scene from left edge".format(pre_state.id))
            explain_success = True
    return explain_success

def explain_for_disappearance_by_occlusion(pre_state, new_depth_frame, new_object_frame):
    new_depth_frame = np.array(new_depth_frame)
    new_object_frame = np.array(new_object_frame)
    explain_success = False
    occluder_pixels = get_occluder_pixels(pre_state.depth, new_depth_frame, new_object_frame)
    # occluder_depth_frame_value = [new_depth_frame[i, j] for i, j in occluder_pixels]
    if pre_state.velocity[0] < 0:
        left_most_object_pixel = min([x[1] for x in pre_state.pixels_on_frame])
        left_occluder_pixels = [x for x in occluder_pixels if x[1] < left_most_object_pixel]
        dis_to_occluder = min([(left_most_object_pixel - x[1]) for x in left_occluder_pixels])
        if dis_to_occluder <= EDGE_MARGIN:
            explain_success = True
            print("Object {} run into occluder from right side".format(pre_state.id))
    elif pre_state.velocity[0] > 0:
        right_most_object_pixel = max([x[1] for x in pre_state.pixels_on_frame])
        right_occluder_pixels = [x for x in occluder_pixels if x[1] > right_most_object_pixel]
        dis_to_occluder = min([(x[1] - right_most_object_pixel) for x in right_occluder_pixels])
        if dis_to_occluder <= EDGE_MARGIN:
            print("Object {} run into occluder from left side".format(pre_state.id))
            explain_success = True
    elif pre_state.velocity[0] == 0 and pre_state.velocity[1] < 0:
        down_most_object_pixel = max([x[0] for x in pre_state.pixels_on_frame])
        down_occluder_pixels = [x for x in occluder_pixels if x[0] > down_most_object_pixel]
        dis_to_occluder = min([(x[0] - down_most_object_pixel) for x in down_occluder_pixels])
        if dis_to_occluder <= EDGE_MARGIN:
            print("Object {} run into occluder from up side".format(pre_state.id))
        explain_success = True
    elif pre_state.velocity == (0,0):
        left_most_object_pixel = min([x[1] for x in pre_state.pixels_on_frame])
        left_occluder_pixels = [x for x in occluder_pixels if x[1] < left_most_object_pixel]
        right_most_object_pixel = max([x[1] for x in pre_state.pixels_on_frame])
        right_occluder_pixels = [x for x in occluder_pixels if x[1] > right_most_object_pixel]
        down_most_object_pixel = max([x[0] for x in pre_state.pixels_on_frame])
        down_occluder_pixels = [x for x in occluder_pixels if x[0] > down_most_object_pixel]
        if len(left_occluder_pixels) == 0:
            assert len(right_occluder_pixels) != 0
            dis_to_occluder = min([(x[1] - right_most_object_pixel) for x in right_occluder_pixels])
            if dis_to_occluder <= EDGE_MARGIN:
                print("Object {} run into occluder from left side".format(pre_state.id))
                pre_state.velocity = (1,0)
                explain_success = True
        elif len(right_occluder_pixels) == 0:
            assert len(left_occluder_pixels) != 0
            dis_to_occluder = min([(left_most_object_pixel - x[1]) for x in left_occluder_pixels])
            if dis_to_occluder <= EDGE_MARGIN:
                explain_success = True
                print("Object {} run into occluder from right side".format(pre_state.id))
                pre_state.velocity = (-1,0)
        elif len(down_occluder_pixels) != 0:
            dis_to_occluder = min([(x[0] - down_most_object_pixel) for x in down_occluder_pixels])
            if dis_to_occluder <= EDGE_MARGIN:
                explain_success = True
                print("Object {} run into occluder from top side".format(pre_state.id))
                pre_state.velocity = (0,-1)
        else:
            print("Object {} run into occluder from unknown side".format(pre_state.id))
            exit(0)
    return explain_success

def check_occluder_is_lifted_up(obj_state, new_depth_frame, new_object_frame):
    new_depth_frame = np.array(new_depth_frame)
    new_object_frame = np.array(new_object_frame)

    occluder_lift_up = False
    occluder_pixels = get_occluder_pixels(obj_state.depth, new_depth_frame, new_object_frame)
    last_depth_frame = np.array(obj_state.last_depth_frame)
    last_object_frame = np.array(obj_state.last_object_frame)
    last_occluder_pixels = get_occluder_pixels(obj_state.depth, last_depth_frame, last_object_frame)
    last_occluder_pixels_bottom = max([x[0] for x in last_occluder_pixels])
    occluder_pixels_bottom = max([x[0] for x in occluder_pixels])
    if last_occluder_pixels_bottom > occluder_pixels_bottom + EDGE_MARGIN:
        occluder_lift_up = True
    return occluder_lift_up


