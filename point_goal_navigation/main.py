
import argparse
import torch
import os

from point_goal_navigation.model import NavigatorResNet
from gym_ai2thor.envs.mcs_nav_env import McsNavEnv
from point_goal_navigation.common.utils import batch_obs, _to_tensor

parser = argparse.ArgumentParser(description='Nav')
parser.add_argument('--seed', type=int, default=1,
                    help='random seed (default: 1)')
parser.add_argument('--max-episode-length', type=int, default=1000,
                    help='maximum length of an episode (default: 1000000)')
parser.add_argument('--no_cuda', action='store_true', help='Disable GPU')
parser.set_defaults(no_cuda=False)


if __name__ == '__main__':
    args = parser.parse_args()
    args.cuda = not args.no_cuda and torch.cuda.is_available()
    if args.cuda:
        print('Using', torch.cuda.get_device_name(0))
        torch.cuda.init()

    torch.manual_seed(args.seed)
    args.config_dict = {'max_episode_length': args.max_episode_length}

    env = McsNavEnv(config_dict=args.config_dict)
    nav = NavigatorResNet(env.observation_spaces, env.action_space, "pointgoal_with_gps_compass")
    if env.rgb_sensor:
        if env.depth_sensor:
            raise NotImplementedError("No rgbd model")
        else:
            raise NotImplementedError("No rgb model")
    else:
        if env.depth_sensor:
            model_file = "gibson-4plus-resnet50.pth"
        else:
            model_file = "gibson-0plus-mp3d-train-val-test-blind.pth"

    nav.load_checkpoint(
        os.path.join(
            os.getcwd(), "algorithms/point_goal_navigation/model/model_pretrained/{}".format(model_file)
        )
    )

    while True:
        print("Episode Start")
        obs = env.reset()
        done = False
        mask = torch.zeros(size=(1,1))
        hidden_states = torch.zeros(size=(nav.actor_critic.net.num_recurrent_layers,1,512))
        prev_action = torch.zeros(1,1)
        while not done:
            batch = batch_obs(obs)
            action, hidden_states = nav.act(batch, hidden_states, prev_action, mask)
            print(action)
            prev_action.copy_(_to_tensor(action))
            mask = torch.ones(size=(1,1))
            obs, _, done, _ = env.step(action)
        print("Episode Finish")





