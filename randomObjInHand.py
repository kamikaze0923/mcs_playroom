from planner.ff_planner_handler import PlanParser
from gym_ai2thor.envs.mcs_env import McsEnv
from metaController.metaController import MetaController
import random
import numpy as np
import PIL.Image as Image
from c_swm.utils import save_list_dict_h5py

def random_pick_up(config):
    obj = random.sample(config['objects'], 1)[0]
    print(obj['id'])
    goal_predicates_str = "\t\t(held agent1 {})\n".format(obj['id'])
    return goal_predicates_str

class Episode_collector:

    ACTION_MAPPING = {
        x:i for i,x in enumerate(["MoveAhead", "RotateLeft", "RotateRight", "LookUp", "LookDown", "PickupObject"])
    }

    def __init__(self):
        self.episode = {'obs': [], 'action': [], 'next_obs': []}
        self.prev_obs = None

    def __len__(self):
        return len(self.episode['action'])

    def add_experience(self, step_output, act):
        obs = Episode_collector.preprocess(step_output.object_mask_list[0])
        if self.prev_obs is not None:
            self.episode['obs'].append(self.prev_obs)
            self.episode['action'].append(self.ACTION_MAPPING[act])
            self.episode['next_obs'].append(obs)

        self.prev_obs = obs

    def tuncate_last_ten(self):
        assert self.__len__() >= 10
        self.episode['obs'] = self.episode['obs'][-10:]
        self.episode['action'] = self.episode['action'][-10:]
        self.episode['next_obs'] = self.episode['next_obs'][-10:]


    @staticmethod
    def preprocess(img):
        img = img.resize((50, 50), Image.ANTIALIAS)
        return np.transpose(np.array(img), (2, 0, 1)) / 255




if __name__ == "__main__":
    import time
    env = McsEnv()

    domain_file = "planner/domains/Playroom_domain.pddl"
    facts_file = "planner/sample_problems/playroom_facts.pddl"

    parser = PlanParser()
    replay_buffer = []
    metaController = MetaController(env)
    episode = 0
    while episode < 100:
        print("Episode: {}".format(episode))
        env.reset()
        PlanParser.scene_config_to_pddl(env.scene_config, random_pick_up(env.scene_config), facts_file)
        result_plan = parser.get_plan_from_file(domain_file, facts_file)
        epsd_collector = Episode_collector()
        for action in result_plan:
            print(action)
            metaController.step(action, epsd_collector)

        if len(epsd_collector) < 10:
            continue
        else:
            epsd_collector.tuncate_last_ten()
            assert len(epsd_collector) == 10
            replay_buffer.append(epsd_collector.episode)
            episode += 1

    # for i in range(len(epsd_collector)):
    #     img = np.concatenate([epsd_collector.episode['obs'][i], epsd_collector.episode['next_obs'][i]], axis=2)
    #     img = np.transpose(img*255, (1,2,0)).astype(np.uint8)
    #     img = Image.fromarray(img)
    #     print("Action: " + str(epsd_collector.episode['action'][i]))
    #     img.show()
    #     time.sleep(0.5)
    # import pickle
    # for i in range(1,6):
    #     file = "part{}.pkl".format(i)
    #     a = pickle.load(open(file, "rb"))
    #     print(len(a))
    #     replay_buffer.extend(a)
    # print(len(replay_buffer))
    print(len(replay_buffer))
    save_list_dict_h5py(replay_buffer, "c_swm/data/playroom_train.h5")


    time.sleep(2)
