from gym_ai2thor.envs.mcs_env import McsEnv
from metaController.metaController import MetaController
import sys
from copy import deepcopy
import json
import os
from planner.ff_planner_handler import PlanParser


if __name__ == "__main__":
    env = McsEnv(interaction_sceces="transferral")
    # env = McsEnv(interaction_sceces="searchObjeInReceptacletraining")
    env.reset()
    # metaController = MetaController(env)
    # result = metaController.excecute()
    # exit(0)

    while env.current_scence <= len(env.all_scenes):
        print(env.current_scence)
        metaController = MetaController(env)
        meta_stage = 0
        search_cnt = 0
        while True:
            print("Meta-Stage: {}".format(meta_stage))
            result_plan = metaController.plan_on_current_state()
            for plan in result_plan:
                print(plan)
                break
            if result_plan[0]['action'] == "LookForObjectInReceptacle":
                new_config = deepcopy(metaController.env.scene_config)
                new_config['performerStart']['position'] = {
                    "x": metaController.env.step_output.position['x'],
                    "y": 0,
                    "z": metaController.env.step_output.position['z']
                }
                new_config['performerStart']['rotation'] = {
                    "y": metaController.env.step_output.rotation
                }
                new_config['goal']['category'] = 'searchObjectInReceptacleTraining'
                new_config['goal']['metadata']['targetReceptacleId'] = PlanParser.map_legal_object_name_back(
                    result_plan[0]['receptacleId']
                )

                file_name = new_config['name'].split(".")[0]
                file_path = os.path.join(
                    'interaction_scenes', 'searchObjectInReceptacleTraining', "{}_{}.json".format(file_name, search_cnt)
                )
                with open(file_path, 'w') as fp:
                    json.dump(new_config, fp, indent=4)
                search_cnt += 1
            success = metaController.step(result_plan[0])
            if not success:
                break
            if result_plan[0]['action'] == "End":
                break
            meta_stage += 1
        # time.sleep(2)
        print("Task Reward: {}".format(metaController.env.step_output.reward))
        sys.stdout.flush()
        env.reset()

