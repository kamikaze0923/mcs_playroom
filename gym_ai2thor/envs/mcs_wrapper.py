class McsWrapper:
    def __init__(self, env):
        self.env = env

    def reset(self):
        self.env.reset()

    def step(self, **kwargs):
        self.env.step(**kwargs)

    @property
    def step_output(self):
        return self.env.step_output

    @property
    def max_reach_distance(self):
        return self.env.controller.MAX_REACH_DISTANCE
