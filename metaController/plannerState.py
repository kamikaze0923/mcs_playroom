from planner.ff_planner_handler import PlanParser
from collections import defaultdict

class GameState:

    AGENT_NAME = "agent1"
    AGENT_Y_INIT = 0.4625

    def __init__(self, config):
        self.face_to_front = False
        self.object_facing = None
        self.object_in_hand = None
        self.knowledge = GameKnowlege()

        self.agent_loc_info = {
            self.AGENT_NAME: (
                config['performerStart']['position']['x'],
                self.AGENT_Y_INIT,
                config['performerStart']['position']['z']
            )
        }
        self.object_loc_info = {}
        self.object_open_close_info = {}
        for obj in config['objects']:
            object_id = PlanParser.create_legal_object_name(obj['id'])
            self.object_loc_info[object_id] = (
                obj['shows'][0]['position']['x'],
                obj['shows'][0]['position']['y'],
                obj['shows'][0]['position']['z'],
            )
            if "opened" in obj:
                self.object_open_close_info[object_id] = obj["opened"]

        self.object_containment_info = defaultdict(lambda : [])
        self.object_knowledge_info = {}

        self.goal_predicate_list = None
        if 'goal' in config:
            print(config['goal']["description"])
            self.goal_category = config['goal']['category']
            self.goal_predicate_list = []
            if self.goal_category == "traversal":
                self.goal_object_id = config['goal']['metadata']['target']['id']
                agent_final_loc = PlanParser.replace_digital_number(
                    "loc|{:.2f}|{:.2f}|{:.2f}".format(
                        self.object_loc_info[self.goal_object_id][0],
                        self.object_loc_info[self.goal_object_id][1],
                        self.object_loc_info[self.goal_object_id][2]
                    )
                )
                self.goal_predicate_list.append(
                    "(agentAtLocation {} {})".format(self.AGENT_NAME, agent_final_loc)
                )
            elif self.goal_category == "retrieval":
                self.goal_object_id = PlanParser.create_legal_object_name(config['goal']['metadata']['target']['id'])
                for obj in config['objects']:
                    if obj['id'] == self.goal_object_id:
                        continue
                    if "openable" in obj and obj["openable"] == True:
                        receptacle_object_id = PlanParser.create_legal_object_name(obj['id'])
                        if obj["type"] == "changing_table":
                            continue
                        self.object_containment_info[self.goal_object_id].append(receptacle_object_id)
                        if "opened" in obj:
                            self.object_open_close_info[receptacle_object_id] = True
                        else:
                            self.object_open_close_info[receptacle_object_id] = False
                self.goal_predicate_list.append(
                    "(held {} {})".format(self.AGENT_NAME, self.goal_object_id)
                )
            elif self.goal_category == "transferral":
                transfer_object_id = config['goal']['metadata']['target_1']['id']
                target_object_id = config['goal']['metadata']['target_2']['id']
                if config['goal']['metadata']['relationship'][1] == "next to":
                    self.goal_predicate_list.append(
                        "(objectNextTo {} {})".format(
                            PlanParser.create_legal_object_name(transfer_object_id),
                            PlanParser.create_legal_object_name(target_object_id)
                        )
                    )
                elif config['goal']['metadata']['relationship'][1] == "on top of":
                    self.goal_predicate_list.append(
                        "(objectOnTopOf {} {})".format(
                            PlanParser.create_legal_object_name(transfer_object_id),
                            PlanParser.create_legal_object_name(target_object_id)
                        )
                    )



class GameKnowlege:
    def __init__(self):
        self.canNotPutin = set()
        self.objectNextTo = {}
        self.objectOnTopOf = {}
