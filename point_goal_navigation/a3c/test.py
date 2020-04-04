"""
Adapted from https://github.com/ikostrikov/pytorch-a3c/blob/master/test.py

Contains the testing loop of the shared model within A3C (no optimisation/backprop needed)
Usually this is run concurrently while training occurs and is useful for tracking progress. But to
save resources we can choose to only test every args.test_sleep_time seconds.
"""

import time

import torch
import torch.nn.functional as F

from gym_ai2thor.envs.mcs_nav_env import McsNavEnv
from gym_ai2thor.utils import CSVLogger
from point_goal_navigation.model.policy import PointNavResNetPolicy

import os
from copy import deepcopy
from point_goal_navigation.common.utils import batch_obs

def test(rank, args, shared_model, counter):
    torch.manual_seed(args.seed + rank)
    env = McsNavEnv(config_dict=args.config_dict)
    env.seed(args.seed + rank)

    model = PointNavResNetPolicy(env.observation_spaces, env.action_space)
    model = model.to(args.device)
    model.eval()

    state = env.reset()
    reward_sum = 0
    done = True

    save = 'steps{}-process{}-lr{}-entropy_coef{}'.format(args.num_steps, args.num_processes,
                                                             args.lr, args.entropy_coef)
    save = os.path.join('logs', save)
    os.makedirs(save, exist_ok=True)

    if args.model:
        shared_model.load_state_dict(torch.load(os.path.join(save, "solved_ai2thor.pth")))
    else:
        logger = CSVLogger(os.path.join(save, 'test.csv'))
        fileds = ['episode_reward', 'frames_rendered']
        logger.log(fileds)

    start_time = time.time()

    episode_length = 0
    while True:
        ckpt_counter = 0
        done_mask = torch.zeros(size=(1,1)).to(args.device)
        undone_mask = torch.ones(size=(1,1)).to(args.device)
        episode_length += 1
        # Sync with the shared model
        if done:
            model.load_state_dict(deepcopy(shared_model.state_dict()))
            rnn_hidden_states = torch.zeros(size=(model.net.num_recurrent_layers, 1, 512)).to(args.device)
            prev_action = torch.zeros(1, 1).to(args.device)
            mask = done_mask
        else:
            rnn_hidden_states = rnn_hidden_states.detach()

        with torch.no_grad():
            batch = batch_obs(state, args.device)
            value, action, action_log_probs, rnn_hidden_states = model.act(batch, rnn_hidden_states, prev_action, mask)
            # torch.cuda.empty_cache()

        prev_action.copy_(action)
        mask = undone_mask

        action_int = action.cpu().numpy()[0][0].item()
        state, reward, done, _ = env.step(action_int)
        done = done or episode_length >= args.max_episode_length
        reward_sum += reward

        if done:
            print("Time {}, num steps over all threads {}, FPS {:.0f}, episode reward {: .2f}, episode length {}".format(
                time.strftime("%Hh %Mm %Ss", time.gmtime(time.time() - start_time)),
                counter.value, counter.value / (time.time() - start_time),
                reward_sum, episode_length))
            if not args.model:
                logger.log(["{: .2f}".format(reward_sum), counter.value])
                torch.save(model.state_dict(), os.path.join(save, "ckpt{}.pth".format(ckpt_counter)))
                # env.close()
                # logger.close()
                # break

            reward_sum = 0
            episode_length = 0
            state = env.reset()
            time.sleep(args.test_sleep_time)
            ckpt_counter += 1

