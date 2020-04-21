from planner.ff_planner_handler import PlanParser
from gym_ai2thor.envs.mcs_env import McsEnv
from metaController.metaController import MetaController



if __name__ == "__main__":
    import time
    env = McsEnv()

    domain_file = "planner/domains/Playroom_domain.pddl"
    facts_file = "planner/sample_problems/playroom_facts.pddl"

    parser = PlanParser()

    goal_predicates_list = [
        "(inReceptacle plate_b box_a)", "(inReceptacle plate_a plate_b)",
        "(inReceptacle bowl_a plate_a)", "(inReceptacle ball_b bowl_a)"
    ]

    goal_predicates_str = "\t\t(and\n" + "".join(["\t\t\t{}\n".format(i) for i in goal_predicates_list]) + "\t\t)\n"

    PlanParser.scene_config_to_pddl(env.scene_config, goal_predicates_str, facts_file)
    result_plan = parser.get_plan_from_file(domain_file, facts_file)

    metaController = MetaController(env)
    for action in result_plan:
        print(action)
        metaController.step(action)
    time.sleep(2)