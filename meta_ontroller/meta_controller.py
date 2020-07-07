from tasks.search_object_in_receptacle.face_turner import FaceTurnerResNet
from a3c.task_util import get_action_space_from_names
from gym_ai2thor.envs.mcs_nav import McsNavWrapper
from gym_ai2thor.envs.mcs_face import McsFaceWrapper
from gym_ai2thor.envs.mcs_obj import McsObjWrapper
from planner.ff_planner_handler import PlanParser
from meta_ontroller.planner_state import GameState
import machine_common_sense
from tasks.bonding_box_navigation_mcs.bonding_box_navigator import BoundingBoxNavigator, SHOW_ANIMATION
from MCS_exploration import sequence_generator, main
import time


def get_goal(goal_string):
    goal = goal_string.split("|")
    _, goal_x, goal_y, goal_z = goal
    goal_x = float(goal_x)
    goal_y = float(goal_y)
    goal_z = float(goal_z)
    return (goal_x, goal_y, goal_z)


class MetaController:
    def __init__(self, env):
        self.env = env
        self.nav_env = McsNavWrapper(env)
        self.face_env = McsFaceWrapper(env)
        self.obj_env = McsObjWrapper(env)

        # self.nav = NavigatorResNet(get_action_space_from_names(self.nav_env.action_names))
        self.nav = BoundingBoxNavigator()
        if isinstance(self.nav, BoundingBoxNavigator):
            self.env.add_obstacle_func = self.nav.add_obstacle_from_step_output
        self.face = FaceTurnerResNet(get_action_space_from_names(self.face_env.action_names))

        self.plannerState = None
        self.sequence_generator_object = sequence_generator.SequenceGenerator(None, self.env.controller)


    def plan_on_current_state(self):
        planner = PlanParser(self.plannerState)
        planner.planner_state_to_pddl(self.plannerState)
        return planner.get_plan()

    def get_inital_planner_state(self, scene_config):
        self.plannerState = GameState(scene_config)

    def step(self, action_dict):
        assert 'action' in action_dict
        if action_dict['action'] == "GotoLocation":
            goal = get_goal(action_dict['location'])
            success_distance = machine_common_sense.mcs_controller_ai2thor.MAX_REACH_DISTANCE - 0.2
            success = self.nav.go_to_goal(
                self.nav_env, goal, success_distance
            )
            if success:
                self.plannerState.agent_loc_info[self.plannerState.AGENT_NAME] = goal
            else:
                print("Navigation Fail")
                return False

        elif action_dict['action'] == "FaceToFront":
            FaceTurnerResNet.look_to_front(self.face_env)
            self.plannerState.face_to_front = True
            self.plannerState.object_facing = None
        elif action_dict['action'] == "FaceToObject":
            goal = get_goal(action_dict['location'])
            FaceTurnerResNet.look_to_direction(self.face_env, goal)
            object_in_view = [PlanParser.create_legal_object_name(obj.uuid) for obj in self.env.step_output.object_list if not obj.held]
            if action_dict['objectId'] in object_in_view:
                self.plannerState.object_facing = action_dict['objectId']
                self.plannerState.face_to_front = False
            else:
                del self.plannerState.object_loc_info[action_dict['objectId']]
                print("Object {} not at {}".format(action_dict['objectId'], action_dict['location']))
            self.plannerState.face_to_front = False
        elif action_dict['action'] == "PickupObject":
            self.obj_env.step("PickupObject", object_id=action_dict['objectId'], from_playroom=self.plannerState.goal_category == "playroom")
            if self.env.step_output.return_status == "SUCCESSFUL":
                self.plannerState.object_in_hand = action_dict['objectId']
                self.plannerState.object_facing = None
                del self.plannerState.object_loc_info[action_dict['objectId']]
                for key, value_list in self.plannerState.object_containment_info.items():
                    for value in value_list:
                        if value == action_dict['objectId']:
                            self.plannerState.object_containment_info[key].remove(value)
            else:
                print("Pickup {} fail!".format(action_dict['objectId']))
                return False
        elif action_dict['action'] == "PutObjectIntoReceptacle":
            self.obj_env.step(
                "PutObjectIntoReceptacle", object_id=action_dict['objectId'],
                receptacleObjectId=action_dict['receptacleId'], from_playroom=self.plannerState.goal_category == "playroom"
            )
            if self.env.step_output.return_status == "SUCCESSFUL":
                self.plannerState.object_in_hand = None
                for _ in range(5):
                    self.env.step(action="Pass")

                self.plannerState.object_containment_info[action_dict['receptacleId']].append(action_dict['objectId'])
                self.plannerState.object_loc_info[action_dict['objectId']] = self.plannerState.object_loc_info[action_dict['receptacleId']]

                for obj in self.plannerState.object_containment_info[action_dict['objectId']]:
                    self.plannerState.object_containment_info[action_dict['receptacleId']].append(obj)
                    self.plannerState.object_loc_info[obj] = self.plannerState.object_loc_info[action_dict['receptacleId']]

            else:
                print("Put object into receptacle fail")
                exit(0)
                # self.plannerState.knowledge.canNotPutin.add((action_dict['objectId'], action_dict['receptacleId']))
        elif action_dict['action'] == "OpenObject":
            self.obj_env.step(
                "OpenObject", object_id=action_dict['objectId'], from_playroom=self.plannerState.goal_category == "playroom"
            )
            if self.env.step_output.return_status == "SUCCESSFUL":
                self.plannerState.object_open_close_info[action_dict['objectId']] = True
            else:
                print("Open {} fail".format(action_dict['objectId']))
                return False
        elif action_dict['action'] == "CloseObject":
            self.obj_env.step(
                "CloseObject", object_id=action_dict['objectId'], from_playroom=self.plannerState.goal_category == "playroom"
            )
            if self.env.step_output.return_status == "SUCCESSFUL":
                self.plannerState.object_open_close_info[action_dict['objectId']] = False
                for _ in range(5):
                    self.env.step(action="Pass")
            else:
                print("Close {} fail".format(action_dict['objectId']))
                return False

        elif action_dict['action'] == "DropObjectNextTo":
            FaceTurnerResNet.look_to_front(self.face_env)

            print("Head_tilt before drop object {}".format(self.env.step_output.head_tilt))
            self.obj_env.step("DropObject", object_id=action_dict['objectId'], from_playroom=self.plannerState.goal_category == "playroom")
            if self.env.step_output.return_status == "SUCCESSFUL":
                self.plannerState.knowledge.objectNextTo[action_dict['goal_objectId']].append(action_dict['objectId'])
                self.plannerState.object_in_hand = None
                print("Drop Successful, if reward 0 then it should be out of range.")

            if self.plannerState.object_in_hand:
                print("DropObject fail")
                return False

        elif action_dict['action'] == "DropObjectOnTopOf":
            self.obj_env.step(
                "PutObjectIntoReceptacle", object_id=action_dict['objectId'],
                receptacleObjectId=action_dict['goal_objectId'], from_playroom=self.plannerState.goal_category == "playroom"
            ) # use magical action at current point
            if self.env.step_output.return_status == "SUCCESSFUL":
                self.plannerState.knowledge.objectOnTopOf[action_dict['goal_objectId']].append(action_dict['objectId'])
                self.plannerState.object_containment_info[action_dict['goal_objectId']].append(action_dict['objectId'])
                self.plannerState.object_loc_info[action_dict['objectId']] = self.plannerState.object_loc_info[action_dict['goal_objectId']]

                for obj in self.plannerState.object_containment_info[action_dict['objectId']]:
                    self.plannerState.knowledge.objectOnTopOf[action_dict['goal_objectId']].append(obj)
                    self.plannerState.object_containment_info[action_dict['goal_objectId']].append(obj)
                    self.plannerState.object_loc_info[obj] = self.plannerState.object_loc_info[action_dict['goal_objectId']]


                self.plannerState.object_in_hand = None
                print("PutObject succeeded! If reward 0 then it is a bug!")
                # assert self.env.step_output.reward == 1
            else:
                print("PutObjectIntoReceptacle {}".format(self.env.step_output.return_status))
                return False
        return True

    def excecute(self, replan=True):
        SUCCESS_FLAG = False
        scene_config = main.explore_scene(self.sequence_generator_object, self.env.step_output)
        if scene_config['goal_found']:
            self.get_inital_planner_state(scene_config)
            if isinstance(self.nav, BoundingBoxNavigator):
                self.nav.clear_obstacle_dict()
            meta_stage = 0
            result_plan = None
            while True:
                print("Meta-Stage: {}".format(meta_stage))
                if not replan:
                    if meta_stage == 0:
                        result_plan = self.plan_on_current_state()
                    if meta_stage == len(result_plan):
                        break
                    print(result_plan[meta_stage])
                    success = self.step(result_plan[meta_stage])
                else:
                    result_plan = self.plan_on_current_state()
                    for plan in result_plan:
                        print(plan)
                        break
                    success = self.step(result_plan[0])
                if not success:
                    break
                if result_plan[0]['action'] == "End":
                    break
                meta_stage += 1

        print("Task Reward: {}\n".format(self.env.step_output.reward))
        time.sleep(2)
        return SUCCESS_FLAG
