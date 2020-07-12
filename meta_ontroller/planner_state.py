from planner.ff_planner_handler import PlanParser
from collections import defaultdict


class GameState:

    AGENT_NAME = "agent1"
    AGENT_Y_INIT = 0.4625
    RECEPTACLE_RELATIONSHIP = {
        'bowl': ['ball', 'apple'],
        'box': ['ball', 'bowl', 'apple'],
        'chair': ['box', 'bowl', 'ball', 'apple']
    }

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
        self.receptacle_info = defaultdict(lambda : [])
        self.object_open_close_info = {}
        for obj in config['objects']:
            for obj_2 in config['objects']:
                if obj['uuid'] == obj_2['uuid']:
                    continue
                for key, value_list in self.RECEPTACLE_RELATIONSHIP.items():
                    if key in obj['uuid']:
                        for one_value in value_list:
                            if one_value in obj_2['uuid']:
                                self.receptacle_info[PlanParser.create_legal_object_name(obj['uuid'])].append(
                                    PlanParser.create_legal_object_name(obj_2['uuid'])
                                )

            object_id = PlanParser.create_legal_object_name(obj['uuid'])
            self.object_loc_info[object_id] = (
                obj['position']['x'],
                obj['position']['y'],
                obj['position']['z'],
            )
            receptacle_object_id = PlanParser.create_legal_object_name(obj['id'])
            if "box" in obj['id']:
                self.object_open_close_info[receptacle_object_id] = False
            else:
                self.object_open_close_info[receptacle_object_id] = None

        self.object_containment_info = defaultdict(lambda : [])

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
                self.goal_predicate_list.append(
                    "(held {} {})".format(self.AGENT_NAME, self.goal_object_id)
                )
            elif self.goal_category == "transferral":
                self.transfer_object_id = PlanParser.create_legal_object_name(
                    config['goal']['metadata']['target_1']['id']
                )
                self.target_object_id = PlanParser.create_legal_object_name(
                    config['goal']['metadata']['target_2']['id']
                )
                if config['goal']['metadata']['relationship'][1] == "next to":
                    self.goal_predicate_list.append(
                        "(objectNextTo {} {})".format(self.transfer_object_id, self.target_object_id)
                    )
                elif config['goal']['metadata']['relationship'][1] == "on top of":
                    self.goal_predicate_list.append(
                        "(objectOnTopOf {} {})".format(self.transfer_object_id, self.target_object_id)
                    )
            elif self.goal_category == "playroom":
                self.transfer_object_id = PlanParser.create_legal_object_name(
                    "box_b"
                )
                self.target_object_id = PlanParser.create_legal_object_name(
                    "chair_b"
                )

                for obj in config['objects']:
                    if "openable" in obj and obj["openable"] == True:
                        receptacle_object_id = PlanParser.create_legal_object_name(obj['id'])
                        if "opened" in obj:
                            self.object_open_close_info[receptacle_object_id] = True
                        else:
                            self.object_open_close_info[receptacle_object_id] = False
                self.apple_a = PlanParser.create_legal_object_name("apple_a")
                self.ball_a = PlanParser.create_legal_object_name("ball_a")
                self.ball_b = PlanParser.create_legal_object_name("ball_b")
                self.bowl_a = PlanParser.create_legal_object_name("bowl_a")
                self.goal_predicate_list.extend(
                    [
                        "(objectOnTopOf {} {})".format(self.apple_a, self.target_object_id),
                        "(objectOnTopOf {} {})".format(self.ball_a, self.target_object_id),
                        "(objectOnTopOf {} {})".format(self.ball_b, self.target_object_id),
                        # "(objectOnTopOf {} {})".format(self.bowl_a, self.target_object_id),
                        # "(objectOnTopOf {} {})".format(self.transfer_object_id, self.target_object_id),
                        # "(inreceptacle {} {})".format(self.apple_a, self.bowl_a),
                        # "(inreceptacle {} {})".format(self.ball_a, self.transfer_object_id),
                        # "(inreceptacle {} {})".format(self.ball_b, self.transfer_object_id),
                        # "(inreceptacle {} {})".format(self.bowl_a, self.transfer_object_id),
                    ]
                )






class GameKnowlege:
    def __init__(self):
        # self.canNotPutin = set()
        self.objectNextTo = defaultdict(lambda : [])
        self.objectOnTopOf = defaultdict(lambda : [])
