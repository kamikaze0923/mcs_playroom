"""
Base class implementation for ai2thor environments wrapper, which adds an openAI gym interface for
inheriting the predefined methods and can be extended for particular tasks.
"""

import os
import platform
import random
import machine_common_sense

class McsEnv:
    """
    Wrapper base class
    """
    def __init__(self, task=None, scene_type=None, seed=None, start_scene_number=0):

        if platform.system() == "Linux":
            app = "unity_app/MCS-AI2-THOR-Unity-App-v0.0.9.x86_64"
        elif platform.system() == "Darwin":
            app = "unity_app/MCSai2thor.app/Contents/MacOS/MCSai2thor"
        else:
            app = None

        os.environ['MCS_CONFIG_FILE_PATH'] = "mcs_config.json"

        self.controller = machine_common_sense.MCS.create_controller(
            os.path.join(app)
        )

        if task and scene_type:
            goal_dir = os.path.join(task, scene_type)
            all_scenes = sorted(os.listdir(goal_dir))
            self.all_scenes = [os.path.join(goal_dir, one_scene) for one_scene in all_scenes]
        else:
            self.all_scenes = [os.path.join("scenes", "playroom.json")]

        self.current_scene = start_scene_number - 1

        if seed:
            random.seed(seed)

        self.add_obstacle_func = None

    def step(self, **kwargs):
        self.step_output = self.controller.step(**kwargs)
        if self.add_obstacle_func:
            self.add_obstacle_func(self.step_output)
        # print(self.step_output.return_status)

    def reset(self, random_init=False, repeat_current=False):
        if not repeat_current:
            if not random_init:
                self.current_scene += 1
                print(self.all_scenes[self.current_scene])
                self.scene_config, status = machine_common_sense.MCS.load_config_json_file(self.all_scenes[self.current_scene])
            else:
                self.current_scene = random.randint(0, len(self.all_scenes) - 1)
                self.scene_config, status = machine_common_sense.MCS.load_config_json_file(self.all_scenes[self.current_scene])
        if "goal" in self.scene_config:
            print(self.scene_config['goal']["description"])
        self.step_output = self.controller.start_scene(self.scene_config)
        # self.step_output = self.controller.step(action="Pass")



if __name__ == '__main__':
    McsEnv()
