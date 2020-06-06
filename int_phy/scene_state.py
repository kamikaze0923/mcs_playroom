from int_phy.object_state import ObjectState
from int_phy.occluder_state import OccluderState
import sys
from int_phy.explain import *
from appearance.utils import object_classes

import torch
from appearance.networks import EmbeddingNet
import os


class SceneState:

    def __init__(self, step_output):
        self.static_object_set = set()
        for obj in step_output.object_list:
            self.static_object_set.add(obj.uuid)

        self.object_state_dict = {}
        self.occluder_state_dict = {}

        self.depth_frame = step_output.depth_mask_list[-1]
        self.object_frame = step_output.object_mask_list[-1]
        self.frame_size = self.object_frame.size
        self.agent_position = step_output.position
        self.appearance_model = EmbeddingNet()
        self.appearance_model.load_state_dict(torch.load(os.path.join("appearance", "pre_trained", "model.pth")))
        self.distributions = []
        distribution_parameters = torch.load(os.path.join("appearance", "pre_trained", "embedding_distribution.pth"))
        for i, _ in enumerate(object_classes):
            mean = distribution_parameters["object_{}_mean".format(i)]
            cov = distribution_parameters["object_{}_cov".format(i)]
            distribution = torch.distributions.MultivariateNormal(loc=mean, covariance_matrix=cov)
            self.distributions.append(distribution)


    def get_new_object_state_dict(self, object_list, new_depth_frame, new_object_frame):
        new_object_state_dict = {}
        for obj in object_list:
            if obj.uuid in self.static_object_set:
                continue
            try: # it is possible to have a obj in step_output but not in object_mask_frame
                obj_state = ObjectState(obj, new_depth_frame, new_object_frame, self.appearance_model)
                new_object_state_dict[obj.uuid] = obj_state
            except:
                print("Unexpected error:\n {}".format(sys.exc_info()))
        return new_object_state_dict

    def get_new_occluder_state_dict(self, structural_object_list, new_depth_frame, new_object_frame):
        new_structrual_object_state_dict = {}
        for obj in structural_object_list:
            if "wall" not in obj.uuid or "occluder" not in obj.uuid:
                continue
            try: # it is possible to have a obj in step_output but not in object_mask_frame
                obj_state = OccluderState(obj, new_depth_frame, new_object_frame, self.agent_position)
                new_structrual_object_state_dict[obj.uuid] = obj_state
            except:
                print("Unexpected error:\n {}".format(sys.exc_info()))
        return new_structrual_object_state_dict

    def update(self, new_step_output):
        print('-'*40)
        new_depth_frame = new_step_output.depth_mask_list[-1]
        new_object_frame = new_step_output.object_mask_list[-1]


        new_object_state_dict = self.get_new_object_state_dict(
            new_step_output.object_list, new_depth_frame, new_object_frame
        )

        new_occluder_state_dict = self.get_new_occluder_state_dict(
            new_step_output.structural_object_list, new_depth_frame, new_object_frame
        )

        for id, state in new_object_state_dict.items():
            if id not in self.object_state_dict: # object appearance
                print("object {} first appears".format(id))
                self.object_state_dict[id] = state
                if not explain_for_first_appearance(state, self.frame_size):
                    print("object {} first appearance VOE".format(id))
                    # exit(0)
            else:
                if self.object_state_dict[id].in_view == False:
                    print("object {} re-appears".format(id))
                    occluder_id = explain_for_re_appearance(
                            state, self.object_state_dict[id], new_occluder_state_dict
                    )
                    if occluder_id != self.object_state_dict[id].occluded_by.id:
                        print("object {} re-appear from a different occluder {}, shoueld be {}, VOE".format(
                            id, occluder_id, self.object_state_dict[id].occluded_by.id
                        ))
                        # exit(0)
                    self.object_state_dict[id].occluded_by = None
                else:
                    pass
                    print("object {} still in view".format(id))
                self.object_state_dict[id].in_view_update(state)

            likelihoods = check_appearance(self.distributions, state, object_classes)
            print("Likelihood of {}: {: .2f}, {}: {: .2f}".format(
                object_classes[0], likelihoods[0], object_classes[1], likelihoods[1]
            ))


        for id, state in self.object_state_dict.items():
            if state.occluded_by:
                if check_occluder_is_lifted_up(state.occluded_by, new_occluder_state_dict):
                    print("object {} not behind {} VOE".format(id, state.occluded_by.id))
                    state.occluded_by = None

        for id, state in self.object_state_dict.items():
            if id not in new_object_state_dict and self.object_state_dict[id].in_view: #only reports when the first time see the object out of view
                print("object {} disappears".format(id))# object disappearance
                if not explain_for_disappearance_by_out_of_scene(state, self.frame_size):
                    occluder_id = explain_for_disappearance_by_occlusion(state, new_occluder_state_dict)
                    if not occluder_id:
                        print("object {} disappearance VOE".format(id))
                        # exit(0)
                        self.object_state_dict[id].out_view_update()
                    else:
                        self.object_state_dict[id].out_view_update(
                            last_seen_state_and_occluders=(state, new_occluder_state_dict[occluder_id])
                        )
                else:
                    self.object_state_dict[id].out_view_update()

        self.object_frame = new_object_frame
        self.depth_frame = new_depth_frame
