import machine_common_sense

class McsWrapper:

    ABS_ROTATION = 10 # same as settings in habitat, right is positive
    ABS_HEADTILT = 10

    def __init__(self, env):
        self.env = env

    def reset(self):
        self.env.reset()

    def step(self, **kwargs):
        self.env.step(**kwargs)

    @property
    def step_output(self):
        return self.env.step_output

