from point_goal_navigation.navigator import NavigatorResNet
from gym_ai2thor.envs.mcs_nav import McsNavWrapper
from gym_ai2thor.envs.mcs_face import McsFaceWrapper
import os

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
        print(model_file)
        self.nav.load_checkpoint(
            os.path.join(
                os.getcwd(), "point_goal_navigation/model/model_pretrained/{}".format(model_file)
            )
        )

    def step(self, action_dict, epsd_collector=None):
        assert 'action' in action_dict
        if action_dict['action'] == "GotoLocation":
            goal = get_goal(action_dict['location'])
            self.nav.go_to_goal(self.nav_env, goal, epsd_collector)
        elif action_dict['action'] == "FaceToObject":
            goal = get_goal(action_dict['location'])
            self.face_env.look_to_direction(goal, epsd_collector)
        elif action_dict['action'] == "PickupObject":
            self.env.step(action="PickupObject", objectId=action_dict['objectId'])
            epsd_collector.add_experience(self.env.step_output, "PickupObject")
        elif action_dict['action'] == "PutObjectIntoReceptacle":
            self.env.step(
                action="PutObject", objectId=action_dict['objectId'], receptacleObjectId=action_dict['receptacleId']
            )
            print(self.env.step_output.return_status)
        elif action_dict['action'] == "FaceToFront":
            self.face_env.look_to_front()
