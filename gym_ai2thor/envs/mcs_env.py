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
    POSSIBLE_INIT_ROTATION = [i*10 for i in range(36)]
    POSSIBLE_INIT = [-4 + i for i in range(9)]

    def __init__(self, interaction_sceces=True):

        if platform.system() == "Linux":
            app = "unity_app/MCS-AI2-THOR-Unity-App-v0.0.4.x86_64"
        elif platform.system() == "Darwin":
            app = "unity_app/MCSai2thor.app/Contents/MacOS/MCSai2thor"
        else:
            app = None

        self.controller = machine_common_sense.MCS.create_controller(
            os.path.join(app)
        )

        if interaction_sceces:
            goal_dir = os.path.join("interaction_scenes", "retrival")
            all_scenes = sorted(os.listdir(goal_dir))
            self.all_scenes = [os.path.join(goal_dir, one_scene) for one_scene in all_scenes]
        else:
            self.all_scenes = [os.path.join("scenes", "playroom.json")]

        self.current_scence = 0
        self.reset()

    def step(self, **kwargs):
        self.step_output = self.controller.step(**kwargs)
        # print(self.step_output.return_status)

    def reset(self, random_init=False):
        self.scene_config, status = machine_common_sense.MCS.load_config_json_file(self.all_scenes[self.current_scence])
        self.current_scence += 1
        if random_init:
            self.rotation_state = random.choice(self.POSSIBLE_INIT_ROTATION)
            self.scene_config["performerStart"]["rotation"] = self.rotation_state
            n_objects = len(self.scene_config["objects"]) + 1
            all_possible_loc = [(i,j) for i in self.POSSIBLE_INIT for j in self.POSSIBLE_INIT]
            randon_sample_init_loc = random.sample(all_possible_loc, n_objects)
            self.scene_config["performerStart"]["position"]["x"] = randon_sample_init_loc[-1][0]
            self.scene_config["performerStart"]["position"]["z"] = randon_sample_init_loc[-1][1]
            for i in range(n_objects - 1):
                self.scene_config["objects"][i]["shows"][0]["position"]["x"] = randon_sample_init_loc[i][0]
                self.scene_config["objects"][i]["shows"][0]["position"]["z"] = randon_sample_init_loc[i][1]

        self.step_output = self.controller.start_scene(self.scene_config)
        self.step_output = self.controller.step(action="Pass")




if __name__ == '__main__':
    McsEnv()
