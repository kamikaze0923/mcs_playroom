from point_goal_navigation.navigator import NavigatorResNet
from gym_ai2thor.envs.mcs_nav import McsNavWrapper
from gym_ai2thor.envs.mcs_face import McsFaceWrapper
from gym_ai2thor.envs.mcs_obj import McsObjWrapper
import os
from planner.ff_planner_handler import PlanParser
from metaController.plannerState import GameState
import machine_common_sense
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
        self.nav = NavigatorResNet(self.nav_env.action_space, "pointgoal_with_gps_compass")
        if self.nav.RGB_SENSOR:
            if self.nav.DEPTH_SENSOR:
                raise NotImplementedError("No rgbd model")
            else:
                raise NotImplementedError("No rgb model")
        else:
            if self.nav.DEPTH_SENSOR:
                model_file = "gibson-4plus-resnet50.pth"
            else:
                model_file = "gibson-0plus-mp3d-train-val-test-blind.pth"
        self.nav.load_checkpoint(
            os.path.join(
                os.getcwd(), "point_goal_navigation/model/model_pretrained/{}".format(model_file)
            )
        )

        self.plannerState = GameState(env.scene_config)
        self.planner = PlanParser(self.plannerState)

    def plan_on_current_state(self):
        self.planner.planner_state_to_pddl(self.plannerState)
        return self.planner.get_plan()

    def step(self, action_dict, epsd_collector=None):
        assert 'action' in action_dict
        if action_dict['action'] == "GotoLocation":
            goal = get_goal(action_dict['location'])
            success = self.nav.go_to_goal(
                self.nav_env, goal, machine_common_sense.mcs_controller_ai2thor.MAX_REACH_DISTANCE, epsd_collector
            )
            if not success:
                print("Navigation Fail")
                return False
            self.plannerState.agent_loc_info[self.plannerState.AGENT_NAME] = goal
            self.plannerState.object_facing = None
        elif action_dict['action'] == "FaceToFront":
            self.face_env.look_to_front()
            self.plannerState.face_to_front = True
            self.plannerState.object_facing = None
        elif action_dict['action'] == "FaceToObject":
            goal = get_goal(action_dict['location'])
            self.face_env.look_to_direction(goal, epsd_collector)
            object_in_view = [PlanParser.create_legal_object_name(obj.uuid) for obj in self.env.step_output.object_list]
            if action_dict['objectId'] in object_in_view:
                self.plannerState.object_facing = action_dict['objectId']
            else:
                del self.plannerState.object_loc_info[action_dict['objectId']]
            self.plannerState.face_to_front = False
        elif action_dict['action'] == "PickupObject":
            self.obj_env.step("PickupObject", object_id=action_dict['objectId'], epsd_collector=epsd_collector)
            if self.env.step_output.return_status == "SUCCESSFUL":
                self.plannerState.object_in_hand = action_dict['objectId']
            else:
                print("Pickup {} fail!".format(action_dict['objectId']))
        elif action_dict['action'] == "PickupObjectFromReceptacle":
            self.obj_env.step("PickupObject", object_id=action_dict['objectId'], epsd_collector=epsd_collector)
            if self.env.step_output.return_status == "SUCCESSFUL":
                self.plannerState.object_in_hand = action_dict['objectId']
            else:
                print("{} not in {}".format(action_dict['objectId'], action_dict['receptacleId']))
                self.plannerState.object_containment_info[action_dict['objectId']].remove(action_dict['receptacleId'])
        elif action_dict['action'] == "PutObjectIntoReceptacle":
            self.obj_env.step(
                "PutObjectIntoReceptacle", object_id=action_dict['objectId'],
                receptacleObjectId=action_dict['receptacleId'], epsd_collector=epsd_collector
            )
            if self.env.step_output.return_status == "SUCCESSFUL":
                self.plannerState.object_in_hand = None
                self.plannerState.object_containment_info[action_dict['objectId']] = action_dict['receptacleId']
            else:
                self.plannerState.knowledge.canNotPutin.add((action_dict['objectId'], action_dict['receptacleId']))
        elif action_dict['action'] == "OpenObject":
            self.obj_env.step("OpenObject", object_id=action_dict['objectId'], epsd_collector=epsd_collector)
            if self.env.step_output.return_status == "SUCCESSFUL":
                self.plannerState.object_open_close_info[action_dict['objectId']] = True
            else:
                print("Open {} fail".format(action_dict['objectId']))
                return False
        elif action_dict['action'] == "DropObjectNextTo":
            while True:
                self.obj_env.step("DropObject", object_id=action_dict['objectId'], epsd_collector=epsd_collector)
                if self.env.step_output.return_status == "SUCCESSFUL":
                    self.plannerState.knowledge.objectNextTo[action_dict['objectId']] = action_dict['goal_objectId']
                    self.plannerState.object_in_hand = None
                    break
                self.env.step(action="MoveBack", amount=0.05)
        elif action_dict['action'] == "DropObjectOnTopOf":
            goal_object_loc = self.plannerState.object_loc_info[action_dict['goal_objectId']]
            agent_x = self.env.step_output.position['x']
            agent_y = self.env.step_output.position['y']
            agent_z = self.env.step_output.position['z']
            for obj in self.env.step_output.object_list:
                if obj.held:
                    hand_x, hand_y, hand_z = obj.position['x'], obj.position['y'], obj.position['z']
            diff_x = hand_x - agent_x
            diff_y = hand_y - agent_y
            diff_z = hand_z - agent_z
            goal_x, goal_y, goal_z = goal_object_loc
            self.nav_env.micro_move(
                self.env, (goal_x - diff_x, goal_y - diff_y, goal_z - diff_z)
            )
            self.obj_env.step("DropObject", object_id=action_dict['objectId'], epsd_collector=epsd_collector)
            if self.env.step_output.return_status == "SUCCESSFUL":
                self.plannerState.knowledge.objectOnTopOf[action_dict['objectId']] = action_dict['goal_objectId']
                self.plannerState.object_in_hand = None
                assert self.env.step_output.reward == 1
        return True

    def excecute(self):
        meta_stage = 0
        while True:
            print("Meta-Stage: {}".format(meta_stage))
            result_plan = self.plan_on_current_state()
            for plan in result_plan:
                print(plan)
                break
            success = self.step(result_plan[0])
            if not success:
                break
            if result_plan[0]['action'] == "End" or self.env.step_output.return_status == "OUT_OF_REACH":
                break
            meta_stage += 1
        # time.sleep(2)
        print("Task Reward: {}".format(self.env.step_output.reward))
        return True
