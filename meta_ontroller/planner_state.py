from planner.ff_planner_handler import PlanParser
from collections import defaultdict
from copy import deepcopy
import json
import os

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
        self.goal_category = None
        self.creat_goal(config)

    def creat_goal(self, config):
        if 'goal' in config:
            self.goal_category = config['goal']['category']
            self.goal_predicate_list = []
            if self.goal_category == "traversal":
                self.goal_object_id = PlanParser.create_legal_object_name(config['goal']['metadata']['target']['id'])
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
                # del self.object_loc_info[self.goal_object_id]
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
                self.transfer_object_id = PlanParser.create_legal_object_name(
                    config['goal']['metadata']['target_1']['id']
                )
                self.target_object_id = PlanParser.create_legal_object_name(config['goal']['metadata']['target_2']['id'])
                target_object_info = config['goal']['metadata']['target_2']['info']
                # if "sofa chair" in target_object_info:
                #     print("Not support put object on sofa chair")
                #     del self.object_loc_info[self.target_object_id]

                for obj in config['objects']:
                    if obj['id'] == self.transfer_object_id:
                        continue
                    if "openable" in obj and obj["openable"] == True:
                        receptacle_object_id = PlanParser.create_legal_object_name(obj['id'])
                        if obj["type"] == "changing_table":
                            print("Not support open changing table {}".format(receptacle_object_id))
                            continue
                        self.object_containment_info[self.transfer_object_id].append(receptacle_object_id)
                        if "opened" in obj:
                            self.object_open_close_info[receptacle_object_id] = True
                        else:
                            self.object_open_close_info[receptacle_object_id] = False

                if config['goal']['metadata']['relationship'][1] == "next to":
                    self.goal_predicate_list.append(
                        "(objectNextTo {} {})".format(self.transfer_object_id, self.target_object_id)
                    )
                elif config['goal']['metadata']['relationship'][1] == "on top of":
                    self.goal_predicate_list.append(
                        "(objectOnTopOf {} {})".format(self.transfer_object_id, self.target_object_id)
                    )
            elif self.goal_category == "searchObjectInReceptacleTraining":
                if "target" in config['goal']['metadata']:
                    self.goal_object_id = PlanParser.create_legal_object_name(config['goal']['metadata']['target']['id'])
                elif "target_1" in config['goal']['metadata']:
                    self.goal_object_id = PlanParser.create_legal_object_name(config['goal']['metadata']['target_1']['id'])
                del self.object_loc_info[self.goal_object_id]
                receptacle_object_id = PlanParser.create_legal_object_name(config['goal']['metadata']['targetReceptacleId'])
                self.object_containment_info[self.goal_object_id].append(receptacle_object_id)
                for obj in config['objects']:
                    if PlanParser.create_legal_object_name(obj['id']) != receptacle_object_id:
                        continue
                    if "opened" in obj:
                        self.object_open_close_info[receptacle_object_id] = True
                    else:
                        self.object_open_close_info[receptacle_object_id] = False
                self.goal_predicate_list.append(
                    "(isOpened {})".format(receptacle_object_id)
                )






class GameKnowlege:
    def __init__(self):
        self.canNotPutin = set()
        self.objectNextTo = {}
        self.objectOnTopOf = {}
