import multiprocessing
import re
import shlex
import subprocess
from planner.utils import replace_location_string
import os

DEBUG = False

CAPS_ACTION_TO_PLAN_ACTION = {
    "GOTOLOCATION": "GotoLocation",
    "FACETOOBJECT": "FaceToObject",
    "PICKUPOBJECT": "PickupObject",
    "PUTOBJECTINTORECEPTACLE": "PutObjectIntoReceptacle",
    "FACETOFRONT": "FaceToFront"
}

def parse_line(line):
    line = re.sub(r"^\s*step|\d+:\s*", "", line)
    line = line.strip()
    line_args = line.split(" ")
    if line_args[0] not in CAPS_ACTION_TO_PLAN_ACTION:
        return None
    action = CAPS_ACTION_TO_PLAN_ACTION[line_args[0]]
    action_dict = {"action": action}

    if action in ["GotoLocation", "FaceToObject"]:
        target_location = replace_location_string(line_args[-1].lower())
        action_dict["location"] = target_location

    elif action in ["PickupObject"]:
        object_id = line_args[-2].lower()
        action_dict["objectId"] = object_id

    elif action in ["PutObjectIntoReceptacle"]:
        object_id = line_args[-3].lower()
        receptacle_id = line_args[-2].lower()
        action_dict["objectId"] = object_id
        action_dict["receptacleId"] = receptacle_id

    return action_dict


def parse_plan(lines):
    plan = []
    for line in lines:
        action_dict = parse_line(line)
        if action_dict is not None:
            plan.append(action_dict)
    return plan


def get_plan_from_file(args):
    domain, filepath, solver_type = args

    try:
        command = "ff_planner/ff -o {:s} -s {:d} -f {:s}".format(domain, solver_type, filepath)
        planner_output = subprocess.check_output(shlex.split(command), timeout=5)
    except subprocess.CalledProcessError as error:
        # Plan is done
        output_str = error.output.decode("utf-8")
        if DEBUG:
            print("output", output_str)
        if "goal can be simplified to FALSE" in output_str or "won't get here: simplify, non logical" in output_str:
            return [{"action": "End", "value": 0}]
        elif "goal can be simplified to TRUE" in output_str:
            return [{"action": "End", "value": 1}]
        elif len(output_str) == 0:
            # Usually indicates segfault with ffplanner
            # This happens when the goal needs an object that hasn't been seen yet like
            # Q: "is there an egg in the garbage can," but no garbage can has been seen.
            print("Empty plan")
            print("Seg Fault")
            return [{"action": "End", "value": 0}]
        else:
            print("problem", filepath)
            print(output_str)
            print("Empty plan")
            return [{"action": "End", "value": 0}]
    except subprocess.TimeoutExpired:
        print("timeout solver", solver_type, "problem", filepath)
        print("Empty plan")
        return ["timeout", {"action": "End", "value": 0}]

    unparsed_plan = planner_output.decode("utf-8").split("\n")

    parsed_plan = parse_plan(unparsed_plan)

    if len(parsed_plan) == 0:
        parsed_plan = [{"action": "End", "value": 1}]
    return parsed_plan

class PlanParser(object):
    def __init__(self):
        self.process_pool = multiprocessing.Pool(3)

    def get_plan_from_file(self, domain_path, filepath):
        parsed_plans = self.process_pool.map(get_plan_from_file, zip([domain_path] * 3, [filepath] * 3, range(3, 6)))
        return self.find_best_plan(parsed_plans)

    def find_best_plan(self, parsed_plans):
        if all([parsed_plan[0] == "timeout" for parsed_plan in parsed_plans]):
            parsed_plan = parsed_plans[0][1:]
        else:
            parsed_plans = [parsed_plan for parsed_plan in parsed_plans if parsed_plan[0] != "timeout"]
            parsed_plan = min(parsed_plans, key=len)
        return parsed_plan

    @staticmethod
    def scene_config_to_pddl(config, goal_predicates_str, fact_file):
        AGENT_Y_INIT = 0.4625
        tittle = "define (problem ball_and_bowl)\n"
        domain = "\t(:domain playroom)\n"
        metric = "\t(:metric minimize (totalCost))\n"

        init_predicates_list = ["(= (totalCost) 0)", "(handEmpty agent1)"]
        object_list = ["agent1 - agent"]


        agent_init = config['performerStart']['position']
        agent_init = PlanParser.replace_digital_number(
            "loc|{:.2f}|{:.2f}|{:.2f}".format(agent_init['x'], AGENT_Y_INIT, agent_init['z'])
        )
        init_predicates_list.append("(agentAtLocation {} {})".format("agent1", agent_init))

        location_list = [agent_init]
        for obj in config['objects']:
            object_list.append("{} - object".format(obj['id']))
            obj_init = obj['shows'][0]['position']
            obj_init = PlanParser.replace_digital_number(
                "loc|{:.2f}|{:.2f}|{:.2f}".format(obj_init['x'], obj_init['y'], obj_init['z'])
            )
            location_list.append(obj_init + " - location")
            init_predicates_list.append("(objectAtLocation {} {})".format(obj['id'], obj_init))
        objects_str = "".join(["\t\t{}\n".format(obj) for obj in object_list + location_list])
        objects = "\t(:objects\n" + objects_str + "\t)\n"

        init_predicates_str = "".join(["\t\t{}\n".format(i) for i in init_predicates_list])
        init_predicates = "\t(:init\n" + init_predicates_str + "\t)\n"

        goal_predicates = "\t(:goal\n" + goal_predicates_str + "\t)\n"
        all = "({}{}{}{}{}{})".format(tittle, domain, metric, objects, init_predicates, goal_predicates)
        with open(fact_file, "w") as f:
            f.write(all)


    @staticmethod
    def replace_digital_number(loc_str):
        return loc_str.replace("-", "_minus_").replace(".", "_dot_").replace("|", "_bar_")





