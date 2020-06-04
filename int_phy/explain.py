from int_phy.occluder_state import get_running_in_occluder_info, get_running_out_occluder_info

EDGE_MARGIN = 50

def explain_for_first_appearance(state, frame_size):
    explain_success = False
    if frame_size[0] - state.pixels_on_frame['x_max'] <= EDGE_MARGIN:
        print("Object {} come from right into scene".format(state.id))
        explain_success = True
    elif state.pixels_on_frame['x_min'] <= EDGE_MARGIN:
        print("Object {} come from left into scene".format(state.id))
        explain_success = True
    if state.pixels_on_frame['y_min'] <= EDGE_MARGIN:
        print("Object {} come from top into scene".format(state.id))
        explain_success = True
    return explain_success

def explain_for_disappearance_by_out_of_scene(pre_state, frame_size):
    explain_success = False
    if frame_size[0] - pre_state.pixels_on_frame['x_max'] <= EDGE_MARGIN:
        assert pre_state.velocity[0] > 0
        print("Object {} come out of scene from right edge".format(pre_state.id))
        explain_success = True
    elif pre_state.pixels_on_frame['x_min'] <= EDGE_MARGIN:
        assert pre_state.velocity[0] < 0
        print("Object {} come out of scene from left edge".format(pre_state.id))
        explain_success = True
    return explain_success


def explain_for_re_appearance(appear_state, estimate_state, new_occluder_state_dict):
    explain_success = False
    distance_to_occluder, occluder_name = get_running_out_occluder_info(new_occluder_state_dict, appear_state, estimate_state)
    if distance_to_occluder <= EDGE_MARGIN:
        print("Object {} run out of {}".format(appear_state.id, occluder_name))
        explain_success = occluder_name
    return explain_success


def explain_for_disappearance_by_occlusion(pre_state, new_occluder_state_dict):
    explain_success = False
    distance_to_occluder, occluder_name = get_running_in_occluder_info(new_occluder_state_dict, pre_state)
    if distance_to_occluder <= EDGE_MARGIN:
        explain_success = occluder_name
        print("Object {} run into {}".format(pre_state.id, occluder_name))
    return explain_success

def check_occluder_is_lifted_up(last_occluder, new_occluder_dict):
    occluder_lift_up = False
    last_occluder_pixels_bottom = last_occluder.pixels_on_frame['y_max']
    occluder_pixels_bottom = new_occluder_dict[last_occluder.id].pixels_on_frame['y_max']
    if last_occluder_pixels_bottom > occluder_pixels_bottom + EDGE_MARGIN:
        occluder_lift_up = True
    return occluder_lift_up


