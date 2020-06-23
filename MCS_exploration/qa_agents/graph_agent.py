import cv2
import numpy as np
import scipy.ndimage
import os
import time

from game_state import GameState
from graph import graph_obj
from navigation import bounding_box_navigator
import constants


class GraphAgent(object):
    def __init__(self, sess,env, reuse=True, num_unrolls=1, game_state=None, net_scope=None):
        '''
        if net_scope is None:
            with tf.name_scope('agent'):
                with tf.variable_scope('nav_global_network', reuse=reuse):
                    self.network = FreeSpaceNetwork(constants.GRU_SIZE, 1, num_unrolls)
                    self.network.create_net()
        else:
            with tf.variable_scope(net_scope, reuse=True):
                self.network = FreeSpaceNetwork(constants.GRU_SIZE, 1, 1)
                self.network.create_net(add_loss=False)
        '''
        self.nav_radius = 0.1
        self.nav = bounding_box_navigator.BoundingBoxNavigator(self.nav_radius)
        if game_state is None:
            self.game_state = GameState(sess=sess,env=env)
            self.game_state.add_obstacle_func = self.nav.add_obstacle_from_step_output
            #self.game_state = GameState(sess=sess,env=env)
        else:
            self.game_state = game_state
        self.action_util = self.game_state.action_util
        self.gt_graph = None
        #self.sess = sess
        self.num_steps = 0
        self.global_step_id = 0
        self.num_unrolls = num_unrolls
        self.pose_indicator = np.zeros((constants.TERMINAL_CHECK_PADDING * 2 + 1,
                                        constants.TERMINAL_CHECK_PADDING * 2 + 1))
        self.times = np.zeros(2)

    def goto(self, action, step_num):
        # Look down
        start_angle = self.game_state.pose[3]
        if start_angle != 60:
            look_action = {'action': 'TeleportFull',
                           'x': self.game_state.pose[0] * constants.AGENT_STEP_SIZE,
                           'y': self.game_state.agent_height,
                           'z': self.game_state.pose[1] * constants.AGENT_STEP_SIZE,
                           'rotateOnTeleport': True,
                           'rotation': self.game_state.pose[2] * 90,
                           'horizon': 60,
                          }
            super(QuestionGameState, self.game_state).step(look_action)

        self.game_state.end_point = (action['x'], action['z'], action['rotation'] / 90)
        self.goal_pose = np.array([self.game_state.end_point[0] - self.game_state.graph.xMin,
                self.game_state.end_point[1] - self.game_state.graph.yMin],
                dtype=np.int32)[:2]
        self.pose = self.game_state.pose
        self.inference()
        plan, path = self.get_plan()
        steps = 0
        invalid_actions = 0

        self.reset(self.game_state.scene_name)

        self.game_state.board = None
        while steps < 20 and len(plan) > 0 and self.is_possible >= constants.POSSIBLE_THRESH:
            t_start = time.time()
            action = plan[0]
            self.step(action)
            invalid_actions += 1 - int(self.game_state.event.metadata['lastActionSuccess'])

            plan, path = self.get_plan()
            steps += 1
            if constants.DRAWING:
                image = self.draw_state()
                if not os.path.exists('visualizations/images'):
                    os.makedirs('visualizations/images')
                cv2.imwrite('visualizations/images/state_%05d.jpg' %
                        (step_num + steps), image[:, :, ::-1])
            self.times[0] += time.time() - t_start

        print('step time %.3f' % (self.times[0] / max(steps, 1)))
        self.times[0] = 0

       # Look back
        if start_angle != 60:
            look_action = {'action': 'TeleportFull',
                           'x': self.game_state.pose[0] * constants.AGENT_STEP_SIZE,
                           'y': self.game_state.agent_height,
                           'z': self.game_state.pose[1] * constants.AGENT_STEP_SIZE,
                           'rotateOnTeleport': True,
                           'rotation': self.game_state.pose[2] * 90,
                           'horizon': start_angle,
                           }
            super(QuestionGameState, self.game_state).step(look_action)
        return steps, invalid_actions

    def inference(self):
        print ("in inference")
        image = self.game_state.s_t[np.newaxis, np.newaxis, ...]

        self.pose_indicator = np.zeros((constants.TERMINAL_CHECK_PADDING * 2 + 1, constants.TERMINAL_CHECK_PADDING * 2 + 1))
        if (abs(self.pose[0] - self.game_state.end_point[0]) <= constants.TERMINAL_CHECK_PADDING and
                abs(self.pose[1] - self.game_state.end_point[1]) <= constants.TERMINAL_CHECK_PADDING):
            self.pose_indicator[
                    self.pose[1] - self.game_state.end_point[1] + constants.TERMINAL_CHECK_PADDING,
                    self.pose[0] - self.game_state.end_point[0] + constants.TERMINAL_CHECK_PADDING] = 1

        self.feed_dict = {
            self.network.image_placeholder: image,
            self.network.action_placeholder: self.action[np.newaxis, np.newaxis, :],
            self.network.pose_placeholder: np.array(self.gt_graph.get_shifted_pose(self.pose))[np.newaxis, np.newaxis, :3],
            self.network.memory_placeholders: self.memory[np.newaxis, ...],
            self.network.gru_placeholder: self.gru_state,
            self.network.pose_indicator_placeholder: self.pose_indicator[np.newaxis, np.newaxis, ...],
            self.network.goal_pose_placeholder: self.goal_pose[np.newaxis, ...],
            }
        if self.num_unrolls is None:
            self.feed_dict[self.network.num_unrolls] = 1

        outputs = self.sess.run(
            [self.network.patch_weights_clipped,
                self.network.gru_state,
                self.network.occupancy,
                self.network.gru_outputs_full,
                self.network.is_possible_sigm,
             ],
            feed_dict=self.feed_dict)

        self.map_weights = outputs[0][0, 0, ...]
        self.game_state.graph.update_graph((self.map_weights, [1 + graph_obj.EPSILON]), self.pose, rows=[0])

        self.gru_state = outputs[1]
        self.occupancy = outputs[2][0, :self.bounds[3], :self.bounds[2], 0] * (self.game_state.graph.memory[:, :, 0] > 1)
        self.memory = outputs[3][0, 0, ...]
        self.is_possible = outputs[4][0, 0]


    def reset(self, scene_name=None, seed=None, config_filename="",event=None):
        if scene_name is not None:
            self.nav.reset()
            if self.game_state.env is not None and type(self.game_state) == GameState:
                self.game_state.reset(scene_name, use_gt=False, seed=seed,config_filename=config_filename,event=event)
            self.gt_graph = graph_obj.Graph('MCS_exploration/layouts/%s-layout_%s.npy' % (scene_name,str(constants.AGENT_STEP_SIZE)), self.action_util, use_gt=True)
            self.bounds = [self.game_state.graph.xMin, self.game_state.graph.yMin,
                self.game_state.graph.xMax - self.game_state.graph.xMin + 1,
                self.game_state.graph.yMax - self.game_state.graph.yMin + 1]
            '''
            if len(self.game_state.end_point) == 0:
                self.game_state.end_point = (self.game_state.graph.xMin + constants.TERMINAL_CHECK_PADDING,
                        self.game_state.graph.yMin + constants.TERMINAL_CHECK_PADDING, 0)
                print ("in agent reset end point set to : " , self.game_state.end_point)
            '''
            self.action = np.zeros(self.action_util.num_actions)
            self.memory = np.zeros((constants.SPATIAL_MAP_HEIGHT, constants.SPATIAL_MAP_WIDTH, constants.MEMORY_SIZE))
            self.gru_state = np.zeros((1, constants.GRU_SIZE))
            self.pose = self.game_state.pose
            self.is_possible = 1
            self.num_steps = 0
            self.times = np.zeros(2)
            self.impossible_spots = set()
            self.visited_spots = set()
        else:
            #print ("")
            self.game_state.reset(event=event)

        #self.goal_pose = np.array([self.game_state.end_point[0] - self.game_state.graph.xMin,
        #        self.game_state.end_point[1] - self.game_state.graph.yMin],
        #        dtype=np.int32)[:2]
        #self.inference()

    def step(self, action):
        t_start = time.time()
        if type(self.game_state) == GameState:
            self.game_state.step(action)
        else:
            super(QuestionGameState, self.game_state).step(action)
        self.times[1] += time.time() - t_start
        self.num_steps += 1
        return
        if self.num_steps % 100 == 0:
            print('game state step time %.3f' % (self.times[1] / (self.num_steps + 1)))
        self.pose = self.game_state.pose
        self.action[:] = 0
        self.action[self.action_util.action_dict_to_ind(action)] = 1
        #self.inference()
        self.global_step_id += 1

        #if not self.game_state.event.metadata['lastActionSuccess']:
        if not self.game_state.event.return_status :
            # Can't traverse here, make sure the weight is correct.
            if self.pose[2] == 0:
                self.gt_graph.update_weight(self.pose[0], self.pose[1] + 1, graph_obj.MAX_WEIGHT)
                spot = (self.pose[0], self.pose[1] + 1)
            elif self.pose[2] == 1:
                self.gt_graph.update_weight(self.pose[0] + 1, self.pose[1], graph_obj.MAX_WEIGHT)
                spot = (self.pose[0] + 1, self.pose[1])
            elif self.pose[2] == 2:
                self.gt_graph.update_weight(self.pose[0], self.pose[1] - 1, graph_obj.MAX_WEIGHT)
                spot = (self.pose[0], self.pose[1] - 1)
            elif self.pose[2] == 3:
                self.gt_graph.update_weight(self.pose[0] - 1, self.pose[1], graph_obj.MAX_WEIGHT)
                spot = (self.pose[0] - 1, self.pose[1])
            self.impossible_spots.add(spot)
        else:
            self.visited_spots.add((self.pose[0], self.pose[1]))
        for spot in self.impossible_spots:
            graph_max = self.gt_graph.memory[:, :, 0].max()
            self.game_state.graph.update_weight(spot[0], spot[1], graph_max)
            #self.occupancy[spot[1], spot[0]] = 1

    def get_plan(self):
        self.plan, self.path = self.game_state.graph.get_shortest_path(self.pose, self.game_state.end_point)
        return self.plan, self.path

    def get_label(self):
        #patch, curr_point = self.gt_graph.get_graph_patch(self.pose)
        patch = self.gt_graph.get_graph_patch(self.pose)
        patch = patch[:, :, 0]
        patch[patch < 2] = 0
        patch[patch > 1] = 1
        return patch

    def draw_state(self, return_list=False):
        if not constants.DRAWING:
            return
        from utils import drawing
        curr_image = self.game_state.detection_image.copy()
        curr_depth = self.game_state.s_t_depth
        if curr_depth is not None:
            curr_depth = self.game_state.s_t_depth.copy()
            curr_depth[0, 0] = 0
            curr_depth[0, 1] = constants.MAX_DEPTH

        label = np.flipud(self.get_label())
        patch = np.flipud(self.game_state.graph.get_graph_patch(self.pose)[0])
        state_image = self.game_state.draw_state().copy()
        memory_map = np.flipud(self.game_state.graph.memory.copy())
        memory_map = np.concatenate((memory_map[:, :, [0]], np.zeros(memory_map[:, :,[0]].shape), memory_map[:, :, 1:]), axis=2)

        images = [
                curr_image,
                state_image,

                np.minimum(memory_map[:, :, 0], 200),
                np.argmax(memory_map[:, :, 1:], axis=2),

                label[:, :],
                np.minimum(patch[:, :, 0], 10),
                ]
        if return_list:
            return images
        action_str = 'action: %s possible %.3f' % (self.action_util.actions[np.where(self.action == 1)[0].squeeze()]['action'], self.is_possible)
        titles = ['%07d' % self.num_steps, action_str, 'Occupancy Map', 'Objects Map', 'Label Patch', 'Learned Patch']
        image = drawing.subplot(images, 4, 3, curr_image.shape[1], curr_image.shape[0],
                titles=titles, border=3)

        return image
