import re
import shlex
import subprocess
from planner.utils import replace_location_string
import multiprocessing
import numpy as np


DEBUG = False

CAPS_ACTION_TO_PLAN_ACTION = {
    "GOTOLOCATION": "GotoLocation",
    "FACETOOBJECT": "FaceToObject",
    "PICKUPOBJECT": "PickupObject",
    # "PICKUPOBJECTFROMRECEPTACLE": "PickupObjectFromReceptacle",
    "LOOKFOROBJECTINRECEPTACLE": "LookForObjectInReceptacle",
    "PUTOBJECTINTORECEPTACLE": "PutObjectIntoReceptacle",
    "FACETOFRONT": "FaceToFront",
    "OPENOBJECT": "OpenObject",
    "CLOSEOBJECT": "CloseObject",
    "DROPOBJECTNEXTTO": "DropObjectNextTo",
    "DROPOBJECTONTOPOF": "DropObjectOnTopOf"
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
        if action == "FaceToObject":
            action_dict["objectId"] = line_args[-2].lower()

    elif action in ["PickupObject", "OpenObject", "CloseObject", "DropObjectNextTo", "DropObjectOnTopOf"]:
        object_id = line_args[-2].lower()
        action_dict["objectId"] = object_id
        if action in ["DropObjectNextTo", "DropObjectOnTopOf"]:
            action_dict["goal_objectId"] = line_args[-3].lower()

    elif action in ["PutObjectIntoReceptacle"]:
        object_id = line_args[-2].lower()
        receptacle_id = line_args[-3].lower()
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
        weight = 1.5
        command = "ff_planner/ff -o {} -f {} -s {} -w {}".format(domain, filepath, solver_type, weight)
        if DEBUG:
            print(command)
        planner_output = subprocess.check_output(shlex.split(command), timeout=200)
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

    GOALS_FILE = "planner/sample_problems/running_goals.pddl"

    def __init__(self, plannerState=None):
        if plannerState.goal_category == "playroom":
            self.domain_file = "planner/domains/Playroom_domain.pddl"
        else:
            self.domain_file = "planner/domains/InteractionScenes_domain.pddl"

        self.goal_predicates = PlanParser.create_goal_str(plannerState.goal_predicate_list)
        self.facts_file = "planner/sample_problems/running_facts_{}.pddl".format(0)


    def get_plan(self):
        process_pool = multiprocessing.Pool(1)
        parsed_plans = process_pool.map(
            get_plan_from_file, zip([self.domain_file] * 3, [self.facts_file] * 3, range(3, 6))
        )
        process_pool.close()
        return self.find_best_plan(parsed_plans)

    def find_best_plan(self, parsed_plans):
        if all([parsed_plan[0] == "timeout" for parsed_plan in parsed_plans]):
            parsed_plan = parsed_plans[0][1:]
        else:
            parsed_plans = [parsed_plan for parsed_plan in parsed_plans if parsed_plan[0] != "timeout"]
            parsed_plan = min(parsed_plans, key=len)
        return parsed_plan

    def planner_state_to_pddl(self, gameState):
        tittle = "define (problem ball_and_bowl)\n"
        domain = "\t(:domain playroom)\n"
        metric = "\t(:metric minimize (totalCost))\n"

        init_predicates_list = ["(= (totalCost) 0)"]
        object_list = ["{} - agent".format(gameState.AGENT_NAME)]
        if gameState.object_in_hand is None:
            init_predicates_list.append("(handEmpty {})".format(gameState.AGENT_NAME))
        else:
            init_predicates_list.append("(held {} {})".format(gameState.AGENT_NAME, gameState.object_in_hand))
            object_list.append("{} - object".format(gameState.object_in_hand))

        if gameState.face_to_front:
            init_predicates_list.append("(headTiltZero {})".format(gameState.AGENT_NAME))

        if gameState.object_facing:
            init_predicates_list.append("(lookingAtObject {} {})".format(gameState.AGENT_NAME, gameState.object_facing))

        for rcp, obj_list in gameState.object_containment_info.items():
            for obj in obj_list:
                init_predicates_list.append("(inReceptacle {} {})".format(obj, rcp))

        # for obj, rcp in gameState.knowledge.canNotPutin:
        #     init_predicates_list.append("(canNotPutin {} {})".format(obj, rcp))

        agent_init_loc = PlanParser.replace_digital_number(
            "loc|{:.2f}|{:.2f}|{:.2f}".format(
                gameState.agent_loc_info[gameState.AGENT_NAME][0],
                gameState.agent_loc_info[gameState.AGENT_NAME][1],
                gameState.agent_loc_info[gameState.AGENT_NAME][2]
            )
        )
        init_predicates_list.append("(agentAtLocation {} {})".format(gameState.AGENT_NAME, agent_init_loc))

        location_list = ["{} - location".format(agent_init_loc)]


        self.generate_interactive_scene_object_str(object_list, location_list, init_predicates_list, gameState)

        objects_str = "".join(["\t\t{}\n".format(obj) for obj in object_list + location_list])
        objects = "\t(:objects\n" + objects_str + "\t)\n"

        init_predicates_str = "".join(["\t\t{}\n".format(i) for i in init_predicates_list])
        init_predicates = "\t(:init\n" + init_predicates_str + "\t)\n"

        all = "({}{}{}{}{}{})".format(tittle, domain, metric, objects, init_predicates, self.goal_predicates)
        with open(self.facts_file, "w") as f:
            f.write(all)


    def generate_interactive_scene_object_str(self, object_list, location_list, init_predicates_list, gameState):
        for obj_key, obj_loc_info in gameState.object_loc_info.items():
            object_list.append("{} - object".format(obj_key))
            obj_init_loc = PlanParser.replace_digital_number(
                "loc|{:.2f}|{:.2f}|{:.2f}".format(obj_loc_info[0], obj_loc_info[1], obj_loc_info[2])
            )
            location_list.append("{} - location".format(obj_init_loc))
            init_predicates_list.append("(objectAtLocation {} {})".format(obj_key, obj_init_loc))

        for obj_key_1, obj_loc_info_1 in gameState.object_loc_info.items():
            obj_init_loc_1 = PlanParser.replace_digital_number(
                "loc|{:.2f}|{:.2f}|{:.2f}".format(obj_loc_info_1[0], obj_loc_info_1[1], obj_loc_info_1[2])
            )
            agent_init_loc = PlanParser.replace_digital_number(
                "loc|{:.2f}|{:.2f}|{:.2f}".format(
                    gameState.agent_loc_info[gameState.AGENT_NAME][0],
                    gameState.agent_loc_info[gameState.AGENT_NAME][1],
                    gameState.agent_loc_info[gameState.AGENT_NAME][2]
                )
            )
            if agent_init_loc != obj_init_loc_1:
                init_dis = np.linalg.norm(np.array(gameState.agent_loc_info[gameState.AGENT_NAME]) - np.array(obj_loc_info_1))
                cost = init_dis
                init_predicates_list.append(
                    "(= (distance {} {}) {:.2f})".format(agent_init_loc, obj_init_loc_1, cost)
                )

            for obj_key_2, obj_loc_info_2 in gameState.object_loc_info.items():
                if obj_key_1 == obj_key_2:
                    continue

                obj_init_loc_2 = PlanParser.replace_digital_number(
                    "loc|{:.2f}|{:.2f}|{:.2f}".format(obj_loc_info_2[0], obj_loc_info_2[1], obj_loc_info_2[2])
                )
                dis = np.linalg.norm(np.array(obj_loc_info_1) - np.array(obj_loc_info_2))
                cost = dis
                init_predicates_list.append(
                    "(= (distance {} {}) {:.2f})".format(obj_init_loc_1, obj_init_loc_2, cost)
                )

        for goal_obj, obj_list in gameState.knowledge.objectNextTo.items():
            for obj in obj_list:
                init_predicates_list.append("(objectNextTo {} {})".format(obj, goal_obj))

        for goal_obj, obj_list in gameState.knowledge.objectOnTopOf.items():
            for obj in obj_list:
                init_predicates_list.append("(objectOnTopOf {} {})".format(obj, goal_obj))

        for obj_canBe_open, isOpen in gameState.object_open_close_info.items():
            if isOpen is not None:
                init_predicates_list.append("(openable {})".format(obj_canBe_open))
                if isOpen:
                    init_predicates_list.append("(isOpened {})".format(obj_canBe_open))

        for receptacle, obj_list in gameState.receptacle_info.items():
            for obj in obj_list:
                init_predicates_list.append("(isReceptacle {} {})".format(receptacle, obj))


    @staticmethod
    def replace_digital_number(loc_str):
        return loc_str.replace("-", "_minus_").replace(".", "_dot_").replace("|", "_bar_")

    @staticmethod
    def create_legal_object_name(obj_str):
        return "legal_" + obj_str.replace("-", "_")

    @staticmethod
    def map_legal_object_name_back(obj_str, from_playroom):
        if not from_playroom:
            legal = obj_str.replace("legal_", "").replace("_", "-")
        else:
            legal = obj_str.replace("legal_", "")
        return legal

    @staticmethod
    def create_goal_str(source):
        if isinstance(source, list):
            string = ["\t(:goal\n", "\t\t(and\n"] \
                                   + ["\t\t\t{}\n".format(p) for p in source] \
                                   + ["\t\t)\n" + "\t)\n"]
        else:
            string = source.readlines()
        return "".join(string)









