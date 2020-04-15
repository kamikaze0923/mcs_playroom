from planner.ff_planner_handler import PlanParser
from gym_ai2thor.envs.mcs_env import McsEnv
from metaController.metaController import MetaController



if __name__ == "__main__":

    parser = PlanParser()
    result_plan = parser.get_plan_from_file(
        "planner/domains/Playroom_domain.pddl", "planner/sample_problems/problem_playroom.pddl"
    )

    import time
    env = McsEnv()
    metaController = MetaController(env)
    for action in result_plan:
        print(action)
        metaController.step(action)
    time.sleep(2)


