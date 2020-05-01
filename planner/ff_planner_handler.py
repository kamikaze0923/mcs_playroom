import multiprocessing
import re
import shlex
import subprocess
from planner.utils import replace_location_string



DEBUG = False

CAPS_ACTION_TO_PLAN_ACTION = {
    "GOTOLOCATION": "GotoLocation",
    "FACETOOBJECT": "FaceToObject",
    "PICKUPOBJECT": "PickupObject",
    "PICKUPOBJECTFROMRECEPTACLE": "PickupObjectFromReceptacle",
    "PUTOBJECTINTORECEPTACLE": "PutObjectIntoReceptacle",
    "FACETOFRONT": "FaceToFront",
    "OPENOBJECT": "OpenObject",
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

    elif action in ["PickupObject", "OpenObject", "DropObjectNextTo", "DropObjectOnTopOf"]:
        object_id = line_args[-2].lower()
        action_dict["objectId"] = object_id
        if action in ["DropObjectNextTo", "DropObjectOnTopOf"]:
            action_dict["goal_objectId"] = line_args[-3].lower()

    elif action in ["PutObjectIntoReceptacle", "PickupObjectFromReceptacle"]:
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

    command = "ff_planner/ff -o {:s} -s {:d} -f {:s}".format(domain, solver_type, filepath)
    proc = subprocess.run(shlex.split(command), stdout=subprocess.PIPE)
    unparsed_plan = proc.stdout.decode("utf-8").split("\n")
    parsed_plan = parse_plan(unparsed_plan)

    if len(parsed_plan) == 0:
        parsed_plan = [{"action": "End", "value": 1}]
    return parsed_plan

class PlanParser(object):

    FACTS_FILE = "planner/sample_problems/running_facts.pddl"
    GOALS_FILE = "planner/sample_problems/running_goals.pddl"
    CONSIDER_OBJECT_TYPES = [
        "ballType", "appleType", "cupType", "boxType", "bowlType",
        "plateType", "sofaType", "sofa_chairType", "chairType"
    ]
    CONSIDER_RECEPTACLE_TYPES = [
        "cupType", "boxType", "bowlType",
        "plateType"
        #, "sofaType", "sofa_chairType"
    ]
    CONSIDER_OPENABLE_TYPES = [
        "boxType"
    ]

    def __init__(self, plannerState=None):
        self.process_pool = multiprocessing.Pool(1)
        if plannerState.goal_predicate_list is None:
            self.goal_predicates = PlanParser.create_goal_str(open(self.GOALS_FILE))
            self.domain_file = "planner/domains/Playroom_domain.pddl"
        else:
            self.goal_predicates = PlanParser.create_goal_str(plannerState.goal_predicate_list)
            if plannerState.goal_category == "traversal":
                self.domain_file = "planner/domains/Traversal_domain.pddl"
            elif plannerState.goal_category == "retrieval":
                self.domain_file = "planner/domains/Retrieval_domain.pddl"
            elif plannerState.goal_category == "transferral":
                self.domain_file = "planner/domains/Transferral_domain.pddl"


    def get_plan(self):
        # parsed_plans = self.process_pool.map(
        #     get_plan_from_file, zip([self.domain_file] * 1, [self.FACTS_FILE] * 1, range(3, 4))
        # )
        parsed_plans = get_plan_from_file((self.domain_file, self.FACTS_FILE, 3))
        return parsed_plans
        # return self.find_best_plan(parsed_plans)

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
        if gameState.object_in_hand is None:
            init_predicates_list.append("(handEmpty {})".format(gameState.AGENT_NAME))
        else:
            init_predicates_list.append("(held {} {})".format(gameState.AGENT_NAME, gameState.object_in_hand))

        if gameState.face_to_front:
            init_predicates_list.append("(headTiltZero {})".format(gameState.AGENT_NAME))

        if gameState.object_facing:
            init_predicates_list.append("(lookingAtObject {} {})".format(gameState.AGENT_NAME, gameState.object_facing))

        object_list = ["{} - agent".format(gameState.AGENT_NAME)]

        if gameState.object_in_hand not in gameState.object_loc_info and gameState.object_in_hand is not None:
            object_list.append("{} - object".format(gameState.object_in_hand))

        for obj, rcp_list in gameState.object_containment_info.items():
            for rcp in rcp_list:
                init_predicates_list.append("(inReceptacle {} {})".format(obj, rcp))
            if obj not in gameState.object_loc_info:
                object_list.append("{} - object".format(obj))

        for obj, rcp in gameState.knowledge.canNotPutin:
            init_predicates_list.append("(canNotPutin {} {})".format(obj, rcp))


        agent_init_loc = PlanParser.replace_digital_number(
            "loc|{:.2f}|{:.2f}|{:.2f}".format(
                gameState.agent_loc_info[gameState.AGENT_NAME][0],
                gameState.agent_loc_info[gameState.AGENT_NAME][1],
                gameState.agent_loc_info[gameState.AGENT_NAME][2]
            )
        )
        init_predicates_list.append("(agentAtLocation {} {})".format(gameState.AGENT_NAME, agent_init_loc))

        location_list = ["{} - location".format(agent_init_loc)]

        object_types = set()

        if gameState.goal_predicate_list is None:
            self.generate_playroom_object_str(object_list, location_list, init_predicates_list, object_types, gameState)
        else:
            self.generate_interactive_scene_object_str(object_list, location_list, init_predicates_list, gameState)

        objects_str = "".join(["\t\t{}\n".format(obj) for obj in object_list + location_list + list(object_types)])
        objects = "\t(:objects\n" + objects_str + "\t)\n"

        init_predicates_str = "".join(["\t\t{}\n".format(i) for i in init_predicates_list])
        init_predicates = "\t(:init\n" + init_predicates_str + "\t)\n"

        all = "({}{}{}{}{}{})".format(tittle, domain, metric, objects, init_predicates, self.goal_predicates)
        with open(self.FACTS_FILE, "w") as f:
            f.write(all)

    def generate_playroom_object_str(self, object_list, location_list, init_predicates_list, object_types, gameState):
        for obj_key, obj_loc_info in gameState.object_loc_info.items():
            obj_type = PlanParser.get_obj_type(obj_key)
            if obj_type not in self.CONSIDER_OBJECT_TYPES:
                continue
            object_list.append("{} - object".format(obj_key))
            obj_init_loc = PlanParser.replace_digital_number(
                "loc|{:.2f}|{:.2f}|{:.2f}".format(obj_loc_info[0], obj_loc_info[1], obj_loc_info[2])
            )
            location_list.append("{} - location".format(obj_init_loc))
            init_predicates_list.append("(objectAtLocation {} {})".format(obj_key, obj_init_loc))

            object_types.add("{} - objType".format(obj_type))
            init_predicates_list.append("(isType {} {})".format(obj_key, obj_type))
            if obj_type in self.CONSIDER_RECEPTACLE_TYPES:
                init_predicates_list.append("(isReceptacle {})".format(obj_key))
            if obj_type in self.CONSIDER_OPENABLE_TYPES:
                init_predicates_list.append("(openable {})".format(obj_key))
                for obj_canBe_open, isOpen in gameState.object_open_close_info.items():
                    if isOpen:
                        init_predicates_list.append("(isOpened {})".format(obj_canBe_open))


    def generate_interactive_scene_object_str(self, object_list, location_list, init_predicates_list, gameState):
        for obj_key, obj_loc_info in gameState.object_loc_info.items():
            object_list.append("{} - object".format(obj_key))
            obj_init_loc = PlanParser.replace_digital_number(
                "loc|{:.2f}|{:.2f}|{:.2f}".format(obj_loc_info[0], obj_loc_info[1], obj_loc_info[2])
            )
            location_list.append("{} - location".format(obj_init_loc))
            init_predicates_list.append("(objectAtLocation {} {})".format(obj_key, obj_init_loc))
        for obj, goal_obj in gameState.knowledge.objectNextTo.items():
            init_predicates_list.append("(objectNextTo {} {})".format(obj, goal_obj))
        for obj, goal_obj in gameState.knowledge.objectOnTopOf.items():
            init_predicates_list.append("(objectOnTopOf {} {})".format(obj, goal_obj))

        for obj_canBe_open, isOpen in gameState.object_open_close_info.items():
            init_predicates_list.append("(openable {})".format(obj_canBe_open))
            if isOpen:
                init_predicates_list.append("(isOpened {})".format(obj_canBe_open))

    @staticmethod
    def get_obj_type(obj_key):
        splits = obj_key.split("_")
        last_split = splits[-1]
        if len(last_split) == 1:
            t = "_".join(splits[:-1])
        else:
            t = obj_key
        return t + "Type"

    @staticmethod
    def replace_digital_number(loc_str):
        return loc_str.replace("-", "_minus_").replace(".", "_dot_").replace("|", "_bar_")

    @staticmethod
    def create_legal_object_name(obj_str):
        return "legal_" + obj_str.replace("-", "_")

    @staticmethod
    def map_legal_object_name_back(obj_str):
        return obj_str.replace("legal_", "").replace("_", "-")

    @staticmethod
    def create_goal_str(source):
        if isinstance(source, list):
            string = ["\t(:goal\n", "\t\t(and\n"] \
                                   + ["\t\t\t{}\n".format(p) for p in source] \
                                   + ["\t\t)\n" + "\t)\n"]
        else:
            string = source.readlines()
        return "".join(string)









