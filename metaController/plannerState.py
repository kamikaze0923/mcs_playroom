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
        for obj in config['objects']:
            self.object_loc_info[obj['id']] = (
                obj['shows'][0]['position']['x'],
                obj['shows'][0]['position']['y'],
                obj['shows'][0]['position']['z'],
            )
        self.object_containment_info = {}
        self.object_knowledge_info = {}

class GameKnowlege:
    def __init__(self):
        self.canNotPutin = set()
