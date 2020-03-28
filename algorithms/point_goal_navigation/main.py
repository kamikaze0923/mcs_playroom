
import argparse
import torch
import os

from algorithms.point_goal_navigation.ppo.navigator import Navigator
from gym_ai2thor.envs.mcs_nav_env import McsNavEnv

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
    for _ in range(100):
        env.step(0)
    a = 1

    nav = Navigator(env.observation_spaces, env.action_space, "point_goal_with_gps_compass")
    nav.load_checkpoint(
        os.path.join(
            os.getcwd(), "algorithms/point_goal_navigation/model_pretrained/blind.pth"
        )
    )



