from planner.ff_planner_handler import PlanParser
from gym_ai2thor.envs.mcs_env import McsEnv
from metaController.metaController import MetaController
import random

def random_pick_up(config):
    obj = random.sample(config['objects'], 1)[0]
    print(obj['id'])
    goal_predicates_str = "\t\t(held agent1 {})\n".format(obj['id'])
    return goal_predicates_str

if __name__ == "__main__":
    import time
    env = McsEnv()

    domain_file = "planner/domains/Playroom_domain.pddl"
    facts_file = "planner/sample_problems/playroom_facts.pddl"

    parser = PlanParser()

    PlanParser.scene_config_to_pddl(env.scene_config, random_pick_up(env.scene_config), facts_file)
    result_plan = parser.get_plan_from_file(domain_file, facts_file)

    metaController = MetaController(env)
    for action in result_plan:
        print(action)
        metaController.step(action)
    time.sleep(2)
