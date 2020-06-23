
import time
import random
import numpy as np
from graph import graph_obj


from utils import game_util
from utils import action_util
from darknet_object_detection import detector
from machine_common_sense import MCS_Step_Output
from machine_common_sense import MCS_Object
from machine_common_sense import MCS_Util
from cover_floor import *
import shapely.geometry.polygon as sp


import constants

assert (constants.SCENE_PADDING == 5)


def wrap_output(scene_event):
    step_output = MCS_Step_Output(
        object_list=retrieve_object_list(scene_event),
    )

    return step_output


def retrieve_object_colors(scene_event):
    # Use the color map for the final event (though they should all be the same anyway).
    return scene_event.events[len(scene_event.events) - 1].object_id_to_color


def retrieve_object_list(scene_event):
    return sorted([retrieve_object_output(object_metadata, retrieve_object_colors(scene_event)) for \
                   object_metadata in scene_event.metadata['objects']
                   if object_metadata['visible'] or object_metadata['isPickedUp']], key=lambda x: x.uuid)


def retrieve_object_output(object_metadata, object_id_to_color):
    material_list = list(filter(MCS_Util.verify_material_enum_string, [material.upper() for material in \
                                                                       object_metadata['salientMaterials']])) if \
    object_metadata['salientMaterials'] is not None else []

    rgb = object_id_to_color[object_metadata['objectId']] if object_metadata['objectId'] in object_id_to_color \
        else [None, None, None]

    bounds = object_metadata['objectBounds'] if 'objectBounds' in object_metadata and \
                                                object_metadata['objectBounds'] is not None else {}

    return MCS_Object(
        uuid=object_metadata['objectId'],
        color={
            'r': rgb[0],
            'g': rgb[1],
            'b': rgb[2]
        },
        # dimensions=(bounds['objectBoundsCorners'] if 'objectBoundsCorners' in bounds else None),
        position=object_metadata['position'],
        visible=(object_metadata['visible'] or object_metadata['isPickedUp'])

    )


def retrieve_position(scene_event):
    return scene_event.metadata['agent']['position']


class GameState(object):
    def __init__(self, sess=None, env=None, depth_scope=None):
        if env == None:
            self.env = game_util.create_env()
        else:
            self.env = env
        self.action_util = action_util.ActionUtil()
        self.local_random = random.Random()
        '''
        if constants.PREDICT_DEPTH:
            from depth_estimation_network import depth_estimator
            if depth_scope is not None:
                with tf.variable_scope(depth_scope, reuse=True):
                    self.depth_estimator = depth_estimator.get_depth_estimator(sess)
            else:
                self.depth_estimator = depth_estimator.get_depth_estimator(sess)
        if constants.OBJECT_DETECTION:
            self.object_detector = detector.get_detector()
        '''
        self.im_count = 0
        self.times = np.zeros((4, 2))
        self.discovered_explored = {}
        self.discovered_objects = []
        self.number_actions = 0
        self.add_obstacle_func = None
        self.goals_found = False
        self.goals = []
        self.world_poly = None
        self.new_found_objects = []
        self.new_object_found = False

    def process_frame(self, run_object_detection=False):
        self.im_count += 1
        # print ("pose b4 manipulation", self.event.pose)
        self.pose = game_util.get_pose(self.event)
        # self.pose,pose_2 = game_util.get_pose(self.event)
        # print ("pose after manipulation", self.pose)
        # print ("pose after own  manipulation", pose_2)
        # print ()
        # for key,items in self.event.metadata.items():
        # print (len(self.event.events))
        i = 0
        # for key,value in self.event.__dict__.items():
        #    if key == "frame" :
        #        print (key,type(value),len(value))#value)
        #        break
        #    i += 1

        return

        # print ("++++++ B$ function call")
        self.s_t_orig = self.event.frame
        self.s_t = game_util.imresize(self.event.frame, (constants.SCREEN_HEIGHT, constants.SCREEN_WIDTH),
                                      rescale=False)
        # print ("========== after function call")
        # print ("size of s_t", len(self.s_t))
        # print ("type of s_t", type(self.s_t))
        # return#
        # print ("predict depth , drawing ", constants.PREDICT_DEPTH,constants.DRAWING)
        if constants.DRAWING:
            self.detection_image = self.s_t_orig.copy()
        if constants.PREDICT_DEPTH:
            print("in predict depth")
            t_start = time.time()
            self.s_t_depth = self.depth_estimator.get_depth(self.s_t)
            self.times[0, 0] += time.time() - t_start
            self.times[0, 1] += 1
            if self.times[0, 1] % 100 == 0:
                print('depth time  %.3f' % (self.times[0, 0] / self.times[0, 1]))
        elif constants.RENDER_DEPTH_IMAGE:
            self.s_t_depth = game_util.imresize(self.event.depth_frame,
                                                (constants.SCREEN_HEIGHT, constants.SCREEN_WIDTH), rescale=False)

        if (constants.GT_OBJECT_DETECTION or constants.OBJECT_DETECTION or
                (constants.END_TO_END_BASELINE and constants.USE_OBJECT_DETECTION_AS_INPUT) and
                not run_object_detection):
            if constants.OBJECT_DETECTION and not run_object_detection:
                # Get detections.

                t_start = time.time()
                boxes, scores, class_names = self.object_detector.detect(
                    game_util.imresize(self.event.frame, (608, 608), rescale=False))
                self.times[1, 0] += time.time() - t_start
                self.times[1, 1] += 1
                if self.times[1, 1] % 100 == 0:
                    print('detection time %.3f' % (self.times[1, 0] / self.times[1, 1]))
                mask_dict = {}
                used_inds = []
                inds = list(range(len(boxes)))
                for (ii, box, score, class_name) in zip(inds, boxes, scores, class_names):
                    if class_name in constants.OBJECT_CLASS_TO_ID:
                        if class_name not in mask_dict:
                            mask_dict[class_name] = np.zeros((constants.SCREEN_HEIGHT, constants.SCREEN_WIDTH),
                                                             dtype=np.float32)
                        mask_dict[class_name][box[1]:box[3] + 1, box[0]:box[2] + 1] += score
                        used_inds.append(ii)
                mask_dict = {k: np.minimum(v, 1) for k, v in mask_dict.items()}
                used_inds = np.array(used_inds)
                if len(used_inds) > 0:
                    boxes = boxes[used_inds]
                    scores = scores[used_inds]
                    class_names = class_names[used_inds]
                else:
                    boxes = np.zeros((0, 4))
                    scores = np.zeros(0)
                    class_names = np.zeros(0)
                masks = [mask_dict[class_name] for class_name in class_names]

                if constants.END_TO_END_BASELINE:
                    self.detection_mask_image = np.zeros(
                        (constants.SCREEN_HEIGHT, constants.SCREEN_WIDTH, len(constants.OBJECTS)), dtype=np.float32)
                    for cls in constants.OBJECTS:
                        if cls not in mask_dict:
                            continue
                        self.detection_mask_image[:, :, constants.OBJECT_CLASS_TO_ID[cls]] = mask_dict[cls]

            else:
                scores = []
                class_names = []
                masks = []
                for (k, v) in self.event.class_masks.items():
                    if k in constants.OBJECT_CLASS_TO_ID and len(v) > 0:
                        scores.append(1)
                        class_names.append(k)
                        masks.append(v)

                if constants.END_TO_END_BASELINE:
                    self.detection_mask_image = np.zeros(
                        (constants.SCREEN_HEIGHT, constants.SCREEN_WIDTH, constants.NUM_CLASSES), dtype=np.uint8)
                    for cls in constants.OBJECTS:
                        if cls not in self.event.class_detections2D:
                            continue
                        for box in self.event.class_detections2D[cls]:
                            self.detection_mask_image[box[1]:box[3] + 1, box[0]:box[2] + 1,
                            constants.OBJECT_CLASS_TO_ID[cls]] = 1

            if constants.RENDER_DEPTH_IMAGE or constants.PREDICT_DEPTH:
                xzy = game_util.depth_to_world_coordinates(self.s_t_depth, self.pose,
                                                           self.camera_height / constants.AGENT_STEP_SIZE)
                max_depth_mask = self.s_t_depth >= constants.MAX_DEPTH
                for ii in range(len(masks)):
                    mask = masks[ii]
                    mask_locs = (mask > 0)
                    locations = xzy[mask_locs, :2]
                    max_depth_locs = max_depth_mask[mask_locs]
                    depth_locs = np.logical_not(max_depth_locs)
                    locations = locations[depth_locs]
                    score = mask[mask_locs]
                    score = score[depth_locs]
                    # remove outliers:
                    locations = locations.reshape(-1, 2)

                    locations = np.round(locations).astype(np.int32)
                    locations -= np.array(self.bounds)[[0, 1]]
                    locations[:, 0] = np.clip(locations[:, 0], 0, self.bounds[2] - 1)
                    locations[:, 1] = np.clip(locations[:, 1], 0, self.bounds[3] - 1)
                    locations, unique_inds = game_util.unique_rows(locations, return_index=True)
                    score = score[unique_inds]

                    curr_score = self.graph.memory[
                        locations[:, 1], locations[:, 0], constants.OBJECT_CLASS_TO_ID[class_names[ii]] + 1]

                    avg_locs = np.logical_and(curr_score > 0, curr_score < 1)
                    curr_score[avg_locs] = curr_score[avg_locs] * .5 + score[avg_locs] * .5
                    curr_score[curr_score == 0] = score[curr_score == 0]
                    self.graph.memory[locations[:, 1], locations[:, 0], constants.OBJECT_CLASS_TO_ID[
                        class_names[ii]] + 1] = curr_score

                    # inverse marked as empty
                    locations = xzy[np.logical_not(mask_locs), :2]
                    max_depth_locs = max_depth_mask[np.logical_not(mask_locs)]
                    depth_locs = np.logical_not(max_depth_locs)
                    locations = locations[depth_locs]
                    locations = locations.reshape(-1, 2)
                    locations = np.round(locations).astype(np.int32)
                    locations[:, 0] = np.clip(locations[:, 0], self.bounds[0], self.bounds[0] + self.bounds[2] - 1)
                    locations[:, 1] = np.clip(locations[:, 1], self.bounds[1], self.bounds[1] + self.bounds[3] - 1)
                    locations = game_util.unique_rows(locations)
                    locations -= np.array(self.bounds)[[0, 1]]
                    curr_score = self.graph.memory[locations[:, 1], locations[:, 0],
                                                   constants.OBJECT_CLASS_TO_ID[class_names[ii]] + 1]
                    replace_locs = np.logical_and(curr_score > 0, curr_score < 1)
                    curr_score[replace_locs] = curr_score[replace_locs] * .8
                    self.graph.memory[locations[:, 1], locations[:, 0],
                                      constants.OBJECT_CLASS_TO_ID[class_names[ii]] + 1] = curr_score
            if constants.DRAWING:
                if constants.GT_OBJECT_DETECTION:
                    boxes = []
                    scores = []
                    class_names = []
                    for k, v in self.event.class_detections2D.items():
                        if k in constants.OBJECT_CLASS_TO_ID and len(v) > 0:
                            boxes.extend(v)
                            scores.extend([1] * len(v))
                            class_names.extend([k] * len(v))
                boxes = np.array(boxes)
                scores = np.array(scores)
                self.detection_image = detector.visualize_detections(self.event.frame, boxes, class_names, scores)

    def reset(self, scene_name=None, use_gt=True, seed=None, config_filename="", event=None):
        if scene_name is None:
            # Do half reset
            action_ind = self.local_random.randint(0, constants.STEPS_AHEAD ** 2 - 1)
            action_x = action_ind % constants.STEPS_AHEAD - int(constants.STEPS_AHEAD / 2)
            action_z = int(action_ind / constants.STEPS_AHEAD) + 1
            x_shift = 0
            z_shift = 0
            if self.pose[2] == 0:
                x_shift = action_x
                z_shift = action_z
            elif self.pose[2] == 1:
                x_shift = action_z
                z_shift = -action_x
            elif self.pose[2] == 2:
                x_shift = -action_x
                z_shift = -action_z
            elif self.pose[2] == 3:
                x_shift = -action_z
                z_shift = action_x
            action_x = self.pose[0] + x_shift
            action_z = self.pose[1] + z_shift
            self.end_point = (action_x, action_z, self.pose[2])
            # print ("in the game state reset end point is : ", self.end_point)

        else:
            # Do full reset
            # self.world_poly = fov.FieldOfView([0, 0, 0], 0, [])
            self.world_poly = sp.Polygon()
            self.goals_found = False
            self.scene_name = scene_name
            self.number_actions = 0
            # print ("Full reset - in the first time of load")
            grid_file = 'MCS_exploration/layouts/%s-layout_%s.npy' % (scene_name, str(constants.AGENT_STEP_SIZE))
            self.graph = graph_obj.Graph(grid_file, self.action_util, use_gt=use_gt)
            if seed is not None:
                self.local_random.seed(seed)
            lastActionSuccess = False
            self.discovered_explored = {}
            self.discovered_objects = []

            self.bounds = [self.graph.xMin, self.graph.yMin,
                           self.graph.xMax - self.graph.xMin + 1,
                           self.graph.yMax - self.graph.yMin + 1]

            # while True :
            # self.event = self.event.events[0]
            if event != None:
                self.event = event
            else:
                self.event = game_util.reset(self.env, self.scene_name, config_filename)
            self.goals = []
            for key, value in self.event.goal.metadata.items():
                if key == "target" or key == "target_1" or key == "target_2":
                    self.goals.append(self.event.goal.metadata[key]["id"])

            for obj in self.event.object_list:
                if obj.uuid not in self.discovered_explored:
                    print("uuid : ", obj.uuid)
                    self.discovered_explored[obj.uuid] = {0: obj.position}
                    self.discovered_objects.append(obj.__dict__)
                    self.discovered_objects[-1]['explored'] = 0
            self.add_obstacle_func(self.event)
            # print("type of event 2 : ", type(self.event))
            lastActionSuccess = self.event.return_status
            # break

        self.process_frame()
        self.board = None
        # print ("end of reset in game state function")

    def step(self, action_or_ind):
        self.new_found_objects = []
        self.new_object_found = False
        if type(action_or_ind) == int:
            action = self.action_util.actions[action_or_ind]
        else:
            action = action_or_ind
        t_start = time.time()

        # print (action)
        # The object nearest the center of the screen is open/closed if none is provided.
        # if (action['action'] == 'OpenObject' or action['action'] == 'CloseObject') and 'objectId' not in action:
        #    game_util.set_open_close_object(action, self.event)

        if action['action'] == 'RotateRight':
            action = "RotateLook, rotation=90"
        elif action['action'] == 'RotateLeft':
            action = "RotateLook, rotation=-90"
        elif action['action'] == 'MoveAhead':
            action = 'MoveAhead, amount=%d' % action['amount']
            # action =  'MoveAhead, amount=0.5'
            # action =  'MoveAhead, amount=0.2'
        elif action['action'] == 'RotateLook':
            if 'rotation' in action and 'horizon' in action:
                action = "RotateLook, rotation=%d, horizon=%d" % (action['rotation'], action['horizon'])
            elif 'rotation' in action:
                action = "RotateLook, rotation=%d" % action['rotation']
            elif 'horizon' in action:
                action = "RotateLook, horizon=%d" % action['horizon']
        elif action['action'] == 'OpenObject':
            action = "OpenObject,objectId=" + str(action["objectId"])
            # print("constructed action for open object", action)
        '''
        '''
        # print (action)
        end_time_1 = time.time()
        action_creation_time = end_time_1 - t_start
        # print ("action creating time",action_creation_time)

        start_2 = time.time()
        self.event = self.env.step(action)
        end_2 = time.time()
        action_time = end_2 - start_2

        # print ("action time", action_time)

        lastActionSuccess = self.event.return_status

        for obj in self.event.object_list:
            if obj.uuid not in self.discovered_explored:
                print("uuid : ", obj.uuid)
                self.discovered_explored[obj.uuid] = {0: obj.position}
                self.discovered_objects.append(obj.__dict__)
                self.new_object_found = True
                self.new_found_objects.append(obj.__dict__)
                self.discovered_objects[-1]['explored'] = 0

        self.add_obstacle_func(self.event)
        self.number_actions += 1

        self.times[2, 0] += time.time() - t_start
        self.times[2, 1] += 1
        # if self.times[2, 1] % 100 == 0:
        #     print('env step time %.3f' % (self.times[2, 0] / self.times[2, 1]))

        # if self.event.metadata['lastActionSuccess']:
        if self.event.return_status:
            self.process_frame()
        else:
            print("Failed status : ", self.event.return_status)

        for elem in self.discovered_explored:
            if elem in self.goals:
                # total_goal_objects_found[scene_type] += 1
                self.goals.remove(elem)

        if len(self.goals) == 0:
            self.goals_found = True

    def draw_state(self):
        from utils import drawing
        scale = 8
        if self.board is None:
            locs = self.graph.points * scale
            self.board = np.zeros(
                ((self.graph.yMax - self.graph.yMin) * scale, (self.graph.xMax - self.graph.xMin) * scale),
                dtype=np.uint8)
            locs -= np.array([self.graph.xMin, self.graph.yMin]) * scale
            for loc in locs:
                drawing.drawRect(self.board, [loc[0], loc[1], loc[0], loc[1]], scale / 2, 4)
            if type(self.end_point) == list:
                for end_point in self.end_point:
                    goal_loc = (np.array(end_point) * np.array([scale, scale, 90]) -
                                np.array([self.graph.xMin, self.graph.yMin, 0]) * scale).astype(int)
                    drawing.drawRect(self.board, [goal_loc[0], goal_loc[1], goal_loc[0], goal_loc[1]], scale / 2, 5)
            else:
                goal_loc = (np.array(self.end_point) * np.array([scale, scale, 90]) -
                            np.array([self.graph.xMin, self.graph.yMin, 0]) * scale).astype(int)
                goal_arrow = [goal_loc[0] + scale / 2 * (goal_loc[2] == 90) - scale / 2 * (goal_loc[2] == 270),
                              goal_loc[1] + scale / 2 * (goal_loc[2] == 0) - scale / 2 * (goal_loc[2] == 180)]
                drawing.drawRect(self.board, [goal_loc[0], goal_loc[1], goal_loc[0], goal_loc[1]], scale / 2, 5)
                drawing.drawRect(self.board, [goal_arrow[0], goal_arrow[1], goal_arrow[0], goal_arrow[1]], scale / 4, 6)

        self.board[np.logical_or(self.board == 2, self.board == 3)] = 4
        curr_point = np.array(self.pose[:3])
        curr_loc = (curr_point * np.array([scale, scale, 90]) -
                    np.array([self.graph.xMin, self.graph.yMin, 0]) * scale).astype(int)
        curr_arrow = [curr_loc[0] + scale / 2 * (curr_loc[2] == 90) - scale / 2 * (curr_loc[2] == 270),
                      curr_loc[1] + scale / 2 * (curr_loc[2] == 0) - scale / 2 * (curr_loc[2] == 180)]
        drawing.drawRect(self.board, [curr_loc[0], curr_loc[1], curr_loc[0], curr_loc[1]], scale / 2, 2)
        drawing.drawRect(self.board, [curr_arrow[0], curr_arrow[1], curr_arrow[0], curr_arrow[1]], scale / 4, 3)
        self.board[0, 0] = 6
        return np.flipud(self.board)

