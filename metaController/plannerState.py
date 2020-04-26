from planner.ff_planner_handler import PlanParser

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
            self.object_loc_info[obj['id']] = (
                obj['shows'][0]['position']['x'],
                obj['shows'][0]['position']['y'],
                obj['shows'][0]['position']['z'],
            )
            if "opened" in obj:
                self.object_open_close_info[obj['id']] = obj["opened"]
        self.object_containment_info = {}
        self.object_knowledge_info = {}

        self.goal_predicate_list = None
        if 'goal' in config:
            print(config['goal']["description"])
            self.goal_category = config['goal']['category']
            self.goal_predicate_list = []
            if self.goal_category == "traversal":
                goal_object_id = config['goal']['metadata']['target']['id']
                agent_final_loc = PlanParser.replace_digital_number(
                    "loc|{:.2f}|{:.2f}|{:.2f}".format(
                        self.object_loc_info[goal_object_id][0],
                        self.object_loc_info[goal_object_id][1],
                        self.object_loc_info[goal_object_id][2]
                    )
                )
                self.goal_predicate_list.append(
                    "(agentAtLocation {} {})".format(self.AGENT_NAME, agent_final_loc)
                )


class GameKnowlege:
    def __init__(self):
        self.canNotPutin = set()
