from gym_ai2thor.envs.mcs_env import McsEnv
import cv2


class McsHumanControlEnv(McsEnv):
    def __init__(self):
        super().__init__()
        self.hand_object = None

    def step(self, action_str, **args):
        if "Move" in action_str:
            self.step_output = self.controller.step(action=action_str, amount=0.25)
        elif "Look" in action_str:
            if action_str == "LookUp":
                self.step_output = self.controller.step(action="RotateLook", horizon=-10)
            elif action_str == "LookDown":
                self.step_output = self.controller.step(action="RotateLook", horizon=10)
            else:
                raise NotImplementedError
        elif "Rotate" in action_str:
            if action_str == "RotateLeft":
                self.step_output = self.controller.step(action="RotateLook", rotation=-10)
            elif action_str == "RotateRight":
                self.step_output = self.controller.step(action="RotateLook", rotation=10)
            else:
                raise NotImplementedError
        elif action_str == "PickupObject":
            self.step_output = self.controller.step(action="PickupObject", **args)
            if self.step_output.return_status == "SUCCESSFUL":
                self.hand_object = args['objectId']
        elif action_str == "PutObject":
            args["objectId"] = self.hand_object
            self.step_output = self.controller.step(action="PutObject", **args)
            if self.step_output.return_status == "SUCCESSFUL":
                self.hand_object = None
        elif action_str == "DropObject":
            args["objectId"] = self.hand_object
            self.step_output = self.controller.step(action="DropObject", **args)
            if self.step_output.return_status == "SUCCESSFUL":
                self.hand_object = None
        elif action_str == "ThrowObject":
            args["objectId"] = self.hand_object
            self.step_output = self.controller.step(action="ThrowObject", **args)
            if self.step_output.return_status == "SUCCESSFUL":
                self.hand_object = None
        elif action_str == "PushObject":
            self.step_output = self.controller.step(action="PushObject", **args)
        elif action_str == "PullObject":
            self.step_output = self.controller.step(action="PullObject", **args)
        elif action_str == "OpenObject":
            self.step_output = self.controller.step(action="OpenObject", **args)
        elif action_str == "CloseObject":
            self.step_output = self.controller.step(action="CloseObject", **args)
        else:
            self.step_output = self.controller.step(action=action_str)


    def print_step_output(self):
        print("- " * 20)
        print("Previous Action Status: {}".format(self.step_output.return_status))
        if hasattr(self.step_output, "reward"):
            print("Previous Reward: {}".format(self.step_output.reward))
        print(
            "Agent at: ({:.2f}, {:.2f}, {:.2f}), HeadTilt: {:.2f}, Rotation: {:.2f}, HandObject: {}".format(
                self.step_output.position['x'],
                self.step_output.position['y'],
                self.step_output.position['z'],
                self.step_output.head_tilt,
                self.step_output.rotation,
                self.hand_object
            )
        )
        print("Visible Objects:")
        for obj in self.step_output.object_list:
            print("Distance {:.3f} to {} ({:.3f},{:.3f},{:.3f})".format(
                obj.distance_in_world, obj.uuid, obj.position['x'], obj.position['y'], obj.position['z'])
            )






if __name__ == '__main__':
    env = McsHumanControlEnv()

    while True:
        env.print_step_output()
        print("- "*10)
        action = input("Enter Action: ")
        if action == "w":
            env.step("MoveAhead")
        elif action == "s":
            env.step("MoveBack")
        elif action == "a":
            env.step("MoveLeft")
        elif action == "d":
            env.step("MoveRight")
        elif action == "q":
            env.step("RotateLeft")
        elif action == "e":
            env.step("RotateRight")
        elif action == "r":
            env.step("LookUp")
        elif action == "f":
            env.step("LookDown")
        elif action == "U":
            obj = input("Pickup Object! Enter the object ID: ")
            env.step("PickupObject", objectId=obj)
        elif action == "I":
            rec = input("Put Object! Enter the receptacle ID: ")
            env.step("PutObject", receptacleObjectId=rec)
        elif action == "O":
            print("Drop Object!")
            env.step("DropObject")
        elif action == "P":
            print("Throw Object!")
            force = input("Throw Object! Enter the force: ")
            env.step("ThrowObject", force=int(force), objectDirectionY=env.step_output.head_tilt)
        elif action == "J":
            obj = input("Push Object! Enter the object ID: ")
            env.step("PushObject", objectId=obj)
        elif action == "K":
            obj = input("Pull Object! Enter the object ID: ")
            env.step("PullObject", objectId=obj)
        elif action == "N":
            obj = input("Open Object! Enter the object ID: ")
            env.step("OpenObject", objectId=obj)
        elif action == "M":
            obj = input("Close Object! Enter the object ID: ")
            env.step("CloseObject", objectId=obj)
        elif action == "L":
            action_command = input("Input pose action:")
            env.step(action_command)
        elif action == "z":
            break
        else:
            print("Invalid Action")












