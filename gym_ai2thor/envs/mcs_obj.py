from gym_ai2thor.envs.mcs_wrapper import McsWrapper
from planner.ff_planner_handler import PlanParser


class McsObjWrapper(McsWrapper):

    def __init__(self, env):
        super().__init__(env)

    def step(self, action, object_id=None, receptacleObjectId=None, from_playroom=None):
        assert object_id is not None
        object_id = PlanParser.map_legal_object_name_back(object_id, from_playroom)
        if action in ["PickupObject", "OpenObject", "DropObject", "CloseObject"]:
            super().step(action=action, objectId=object_id)
        elif action == "PutObjectIntoReceptacle":
            assert receptacleObjectId is not None
            receptacleObjectId = PlanParser.map_legal_object_name_back(receptacleObjectId, from_playroom)
            super().step(action="PutObject", objectId=object_id, receptacleObjectId=receptacleObjectId)
