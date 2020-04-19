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

    def __init__(self):

        if platform.system() == "Linux":
            app = "gym_ai2thor/unity_app/MCS-AI2-THOR-Unity-App-v0.0.2.x86_64"
        elif platform.system() == "Darwin":
            app = "gym_ai2thor/unity_app/MCSai2thor.app/Contents/MacOS/MCSai2thor"
        else:
            app = None

        self.controller = machine_common_sense.MCS_Controller_AI2THOR(
            os.path.join(app)
        )

        self.scene_config, status = machine_common_sense.MCS.load_config_json_file(
            os.path.join("gym_ai2thor/scenes/playroom_simplified.json")
        )

        self.step_output = None
        self.reset()

    def step(self, **kwargs):
        self.step_output = self.controller.step(**kwargs)
        # print(self.step_output.return_status)

    def reset(self, random_init=True):
        if random_init:
            self.rotation_state = random.sample(self.POSSIBLE_INIT_ROTATION, 1)[0]
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






if __name__ == '__main__':
    McsEnv()
