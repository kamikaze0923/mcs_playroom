from gym_ai2thor.envs.mcs_nav_env import McsEnv


class McsHumanControlEnv(McsEnv):
    def __init__(self):
        super().__init__()

    def step(self, action_str):
        if "Move" in action_str:
            self.controller.step(action=action_str, amount=0.25)
        elif "Look" in action_str:
            if action_str == "LookUp":
                self.controller.step(action="RotateLook", horizon=-10)
            elif action_str == "LookDown":
                self.controller.step(action="RotateLook", horizon=10)
            else:
                raise NotImplementedError
        elif "Rotate" in action_str:
            if action_str == "RotateLeft":
                self.controller.step(action="RotateLook", rotation=-10)
            elif action_str == "RotateRight":
                self.controller.step(action="RotateLook", rotation=10)
            else:
                raise NotImplementedError
        else:
            raise NotImplementedError




if __name__ == '__main__':
    env = McsHumanControlEnv()
    env.reset() # set goal internally

    while True:
        action = input()
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
        elif action == "z":
            break
        else:
            print("Invalid Action")
        print(env.step_output.return_status)










