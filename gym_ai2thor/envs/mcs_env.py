"""
Base class implementation for ai2thor environments wrapper, which adds an openAI gym interface for
inheriting the predefined methods and can be extended for particular tasks.
"""

import os
import platform


import machine_common_sense

class McsEnv:
    """
    Wrapper base class
    """
    POSSIBLE_INIT_ROTATION = [i*10 for i in range(360)]
    POSSIBLE_INIT_X = [-4, -3, 3, 4]
    POSSIBLE_INIT_Z = [-4, -3, 3, 4]

    def __init__(self):

        if platform.system() == "Linux":
            app = "gym_ai2thor/unity_app/MCS-AI2-THOR-Unity-App-v0.0.2.x86_64"
        elif platform.system() == "Darwin":
            app = "gym_ai2thor/unity_app/MCSai2thor.app/Contents/MacOS/MCSai2thor"
        else:
            app = None

        self.controller = machine_common_sense.MCS_Controller_AI2THOR(
            os.path.join(os.getcwd(), app),
            # renderDepthImage=self.depth_sensor, renderObjectImage=True
        )

        self.scene_config, status = machine_common_sense.MCS.load_config_json_file(
            os.path.join(os.getcwd(), "gym_ai2thor/scenes/playroom.json")
        )

        self.step_output = None
        self.reset()


    def step(self, **kwargs):
        self.step_output = self.controller.step(**kwargs)

    def reset(self):
        # self.rotation_state = random.sample(self.POSSIBLE_INIT_ROTATION, 1)[0]
        # init_x = random.sample(self.POSSIBLE_INIT_X, 1)[0]
        # init_z = random.sample(self.POSSIBLE_INIT_Z, 1)[0]
        # self.scene_config["performerStart"] = {
        #     "position": {
        #         "x": init_x,
        #         "z": init_z
        #     },
        #     "rotation": {
        #         "y": self.rotation_state
        #     }
        # }
        self.rotation_state = 90
        init_x = 2
        init_z = -2
        self.scene_config["performerStart"] = {
            "position": {
                "x": init_x,
                "z": init_z,
            },
            "rotation": {
                "y": self.rotation_state
            }
        }
        self.step_output = self.controller.start_scene(self.scene_config)


    # def get_rgb(self):
    #     img = self.step_output.image_list[0].convert(mode="P").convert("RGB")
    #     img = np.array(img).transpose(2, 0, 1)
    #     return img
    #
    # def get_depth_rgb(self):
    #     img1 = self.get_rgb()
    #     assert self.depth_sensor
    #     img2 = self.step_output.depth_mask_list[0].convert(mode="L").convert("RGB")
    #     img2 = np.array(img2).transpose(2, 0, 1)
    #     img = np.concatenate([img1, img2], axis=2)
    #     return img





if __name__ == '__main__':
    McsEnv()
