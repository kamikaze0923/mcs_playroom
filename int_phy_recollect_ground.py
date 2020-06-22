from gym_ai2thor.envs.mcs_env import McsEnv
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
import torch
import os
import matplotlib.pyplot as plt
import numpy as np

GROUND_MIN_X = -6.5
GROUND_MAX_X = 6.5
GROUND_STEP_SIZE = 0.01

# SCENE_TYPES = ["object_permanence", "shape_constancy", "spatio_temporal_continuity", "gravity"]
SCENE_TYPES = ["gravity"]
SHAPE_TYPES = ["cylinder", "sphere", "cube"]
DATA_SAVE_DIR = os.path.join("int_phy", "locomotion", "positions")

WITH_OCCLUDER = False
SAVE_SCENE_LENGTH = 40

TOTAL_SCENE = 1080 # max 1080
assert TOTAL_SCENE % SAVE_SCENE_LENGTH == 0
N_RESTART = TOTAL_SCENE // SAVE_SCENE_LENGTH

def get_ground_feature(step_output):
    grounds = list(filter(lambda x: "floor" in x.uuid, step_output.structural_object_list))
    assert len(grounds) == 1
    ramps = list(filter(lambda x: "ramp" in x.uuid, step_output.structural_object_list))
    support_objs = grounds + ramps
    polygons = []
    for obj in support_objs:
        # print(obj.uuid)
        polygon_points = []
        for p in obj.dimensions:
            px = min(6.5, p['x'])
            px = max(-6.5, px)
            py = min(5, p['y'])
            py = max(-1, py)
            polygon_points.append(Point(px, py))
        poly = Polygon(polygon_points)
        polygons.append(poly.convex_hull)

    union_polygon = unary_union(polygons)

    x,y = union_polygon.exterior.xy
    x,y = np.array(x), np.array(y)
    valid = (y >= 0)
    x,y = x[valid], y[valid]

    # plt.cla()
    # plt.plot(x,y)
    # plt.axis('equal')
    # plt.pause(0.5)

    multi_lines = MultiStraightLine(x, y)
    xs = np.arange(GROUND_MIN_X, GROUND_MAX_X+GROUND_STEP_SIZE, GROUND_STEP_SIZE)
    ys = [multi_lines.get_y(i) for i in xs]
    return torch.tensor(ys)



class StraightLine:
    def __init__(self, p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        assert x1 != x2
        self.k = (y2 - y1) / (x2 - x1)
        self.b = y1 - self.k * x1

    def get_y(self, x):
        return self.k * x + self.b


class MultiStraightLine:
    def __init__(self, xs, ys):
        self.ranges = []
        self.lines = []
        assert len(xs) == len(ys)
        for i in range(len(xs) - 1):
            if abs(xs[i] - xs[i+1]) < 1e-4:
                xs[i+1] = xs[i]
                continue
            self.ranges.append((xs[i], xs[i+1]))
            self.lines.append(
                StraightLine((xs[i], ys[i]), (xs[i+1], ys[i+1]))
            )

    def get_y(self, x):
        for (x_min, x_max), line in zip(self.ranges, self.lines):
            if x_min <= x and x < x_max:
                return line.get_y(x)
        raise ValueError('x not in range')





if __name__ == "__main__":
    for scene_type in SCENE_TYPES:
        for _, shape_type in enumerate(SHAPE_TYPES):
            os.makedirs(os.path.join(DATA_SAVE_DIR, "ground", shape_type, scene_type), exist_ok=True)

        object_locomotions = {}
        start_scene_number = 0
        for n_restart in range(N_RESTART):
            object_locomotions = {}
            for _, shape_type in enumerate(SHAPE_TYPES):
                object_locomotions[shape_type] = []

            env = McsEnv(task="intphys_scenes", scene_type=scene_type, start_scene_number=start_scene_number)
            start_scene_number += SAVE_SCENE_LENGTH
            for _ in range(SAVE_SCENE_LENGTH):
                env.reset(random_init=False)
                env_new_objects = []
                env_occluders = []
                env_ramps = []
                for obj in env.scene_config['objects']:
                    if "occluder" in obj['id']:
                        env_occluders.append(obj)
                        continue
                    if "ramp" in obj['id']:
                        env_ramps.append(obj)
                        continue
                    if obj['type'] in SHAPE_TYPES:
                        env_new_objects.append(obj)
                for one_obj in env_new_objects:
                    env.scene_config['objects'] = [one_obj] + env_ramps
                    env.step_output = env.controller.start_scene(env.scene_config)
                    ground_feature = get_ground_feature(env.step_output)
                    object_locomotions[one_obj['type']].append(ground_feature)

            for _, shape_type in enumerate(SHAPE_TYPES):
                padded_ground = torch.stack(object_locomotions[shape_type])
                print("{}, {}".format(shape_type, padded_ground.size()))
                torch.save(padded_ground, os.path.join(DATA_SAVE_DIR, "ground", shape_type, scene_type, "{}.pth".format(n_restart)))

            env.controller.end_scene(None, None)






