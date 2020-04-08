from point_goal_navigation.model.policy import PointNavResNetPolicy
from gif_generator.make_gif import list_of_numpy_to_gif

class NavigatorResNet:
    def __init__(self, observation_space, action_space, goal_sensor_uuid):
        self.actor_critic = PointNavResNetPolicy(
            observation_space,
            action_space,
            goal_sensor_uuid
        )

    def act(self, obs, hidden_states, prev_action, mask):
        _, action, _, rnn_hidden_states = self.actor_critic.act(obs, hidden_states, prev_action, mask, deterministic=False)
        return action[0].item(), rnn_hidden_states

    def load_checkpoint(self, checkpoint_path):
        ckpt = torch.load(checkpoint_path, map_location='cpu')
        self.actor_critic.load_state_dict(
            {
                k[len("actor_critic."):]: v
                for k, v in ckpt["state_dict"].items()
                if "actor_critic" in k
            },
            strict=False
        )


import argparse
import torch
import os

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

    while True:
        print("Episode Start")
        obs = env.reset()
        done = False
        mask = torch.zeros(size=(1,1))
        hidden_states = torch.zeros(size=(nav.actor_critic.net.num_recurrent_layers,1,512))
        prev_action = torch.zeros(1,1)
        episode_image = []
        while not done:
            batch = batch_obs(obs)
            # episode_image.append(env.get_depth_rgb())
            # print(batch['pointgoal_with_gps_compass'])
            action, hidden_states = nav.act(batch, hidden_states, prev_action, mask)
            prev_action.copy_(_to_tensor(action))
            mask = torch.ones(size=(1,1))
            obs, _, done, _ = env.step(action)
        print("Episode Finish")
        # list_of_numpy_to_gif(episode_image, "episode_gif/1.gif")







