from copy import deepcopy
import sys
from int_phy.explain import *


class SceneState:
    def __init__(self, step_output):
        self.static_object_set = set()
        for obj in step_output.object_list:
            self.static_object_set.add(obj.uuid)

        self.object_state_dict = {}
        self.depth_frame = step_output.depth_mask_list[-1]
        self.object_frame = step_output.object_mask_list[-1]
        self.frame_size = self.object_frame.size


    def update(self, new_step_output):
        new_object_state_dict = {}
        new_depth_frame = new_step_output.depth_mask_list[-1]
        new_object_frame = new_step_output.object_mask_list[-1]
        for obj in new_step_output.object_list:
            if obj.uuid in self.static_object_set:
                continue
            try: # it is possible to have a obj in step_output but not in object_mask_frame
                obj_state = ObjectState(obj, new_depth_frame, new_object_frame)
                new_object_state_dict[obj.uuid] = obj_state
            except:
                print("Unexpected error:\n {}".format(sys.exc_info()))


        for id, state in self.object_state_dict.items():
            if id not in new_object_state_dict and self.object_state_dict[id].in_view: #only reports when the first time see the object out of view
                print("object {} disappears".format(id))# object disappearance
                if not explain_for_disappearance_by_out_of_scene(state, self.frame_size):
                    if not explain_for_disappearance_by_occlusion(state, new_depth_frame, new_object_frame):
                        print("Object {} disappearance VOE".format(id))
                        # exit(0)
                        self.object_state_dict[id].out_view_update()
                    else:
                        self.object_state_dict[id].out_view_update(
                            last_seen_state_and_frames=(state, self.object_frame, self.depth_frame)
                        )
                        self.object_state_dict[id].is_occluded = True
                else:
                    self.object_state_dict[id].out_view_update()


        for id, state in new_object_state_dict.items():
            if id not in self.object_state_dict: # object appearance
                print("object {} first appears".format(id))
                self.object_state_dict[id] = state
                if not explain_for_first_appearance(state, self.frame_size):
                    print("Object {} first appearance VOE".format(id))
                    # exit(0)
            else:
                if self.object_state_dict[id].in_view == False:
                    print("object {} re-appears".format(id))
                    if not explain_for_re_appearance(
                            state, self.object_state_dict[id].last_scene_state, new_depth_frame, new_object_frame
                    ):
                        print("Object {} re-appearance VOE".format(id))
                        # exit(0)
                    else:
                        self.object_state_dict[id].is_occluded = False
                else:
                    print("object {} still in view".format(id))
                self.object_state_dict[id].in_view_update(state)

        for id, state in self.object_state_dict.items():
            if state.is_occluded:
                if check_occluder_is_lifted_up(state.last_scene_state, new_depth_frame, new_object_frame):
                    print("Object {} not behind occluder VOE".format(id))
                    state.is_occluded = False

        self.object_frame = new_object_frame
        self.depth_frame = new_depth_frame



class ObjectState:
    def __init__(self, object_info, depth_frame, object_frame):
        self.id = object_info.uuid
        self.position = [object_info.position['x'], object_info.position['y'], object_info.position['z']]
        self.depth, self.pixels_on_frame = get_object_frame_info(object_info, depth_frame, object_frame)
        self.velocity = (0, 0)
        self.in_view = True
        self.is_occluded = False
        self.out_of_view = False
        self.shape = get_object_dimension(object_info.dimensions)
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

    def out_view_update(self, last_seen_state_and_frames=None, constant_velocity=True):
        if last_seen_state_and_frames:
            last_seen_state, last_object_frame, last_depth_frame = last_seen_state_and_frames
            self.last_scene_state = deepcopy(last_seen_state)
            self.last_scene_state.last_object_frame = last_object_frame
            self.last_scene_state.last_depth_frame = last_depth_frame

        if constant_velocity:
            self.position[0] += self.velocity[0]
            self.position[1] += self.velocity[1]

        self.pixels_on_frame = None
        self.in_view = False

