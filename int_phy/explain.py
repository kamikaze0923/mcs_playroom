from int_phy.occluder_state import get_running_in_occluder_info, get_running_out_occluder_info
import torch


EDGE_MARGIN = 50

def explain_for_first_appearance(state, frame_size):
    explain_success = False
    if frame_size[0] - state.edge_pixels['x_max'] <= EDGE_MARGIN:
        print("object {} come from right into scene".format(state.id))
        explain_success = True
    elif state.edge_pixels['x_min'] <= EDGE_MARGIN:
        print("object {} come from left into scene".format(state.id))
        explain_success = True
    if state.edge_pixels['y_min'] <= EDGE_MARGIN:
        print("object {} come from top into scene".format(state.id))
        explain_success = True
    return explain_success

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

def check_occluder_is_lifted_up(last_occluder, new_occluder_dict):
    occluder_lift_up = False
    last_occluder_pixels_bottom = last_occluder.edge_pixels['y_max']
    occluder_pixels_bottom = new_occluder_dict[last_occluder.id].edge_pixels['y_max']
    if last_occluder_pixels_bottom > occluder_pixels_bottom + EDGE_MARGIN:
        occluder_lift_up = True
    return occluder_lift_up


def check_appearance(distributions, appearance, object_classes):
    likelihoods = []
    max_prob_class = None
    max_prob = 0
    for distribution, class_name in zip(distributions, object_classes):
        log_prob = distribution.log_prob(appearance)
        prob = torch.exp(log_prob)
        likelihoods.append(prob)
        print("likelihood of {}: {: .2f}".format(class_name, prob))
        if prob > max_prob:
            max_prob = prob
            max_prob_class = class_name
    print("object type decision: {}".format(max_prob_class))
    return likelihoods


def check_object_patially_occlusion(all_occluder_dict, object_state, frame_size):
    is_partially_occluded = False
    if object_state.edge_pixels['x_min'] == 0 or object_state.edge_pixels['y_min'] == 0:
        is_partially_occluded = True
    elif object_state.edge_pixels['x_max'] == frame_size[0] - 1 or object_state.edge_pixels['y_max'] == frame_size[1] - 1:
        is_partially_occluded = True
    else:
        for _, occluder_state in all_occluder_dict.items():
            if object_state.edge_pixels['x_min'] == occluder_state.edge_pixels['x_max'] + 1:
                is_partially_occluded = True
            elif object_state.edge_pixels['x_max'] == occluder_state.edge_pixels['x_min'] - 1:
                is_partially_occluded = True
            elif object_state.edge_pixels['y_min'] == occluder_state.edge_pixels['y_max'] + 1:
                is_partially_occluded = True
            elif object_state.edge_pixels['y_max'] == occluder_state.edge_pixels['y_min'] - 1:
                is_partially_occluded = True
    return is_partially_occluded


