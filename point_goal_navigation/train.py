"""
Adapted from https://github.com/ikostrikov/pytorch-a3c/blob/master/train.py

Contains the train code run by each A3C process on AI2ThorEnv.
For initialisation, we set up the environment, seeds, shared model and optimizer.
In the main training loop, we always ensure the weights of the current model are equal to the
shared model. Then the algorithm interacts with the environment args.num_steps at a time,
i.e it sends an action to the env for each state and stores predicted values, rewards, log probs
and entropies to be used for loss calculation and backpropagation.
After args.num_steps has passed, we calculate advantages, value losses and policy losses using
Generalized Advantage Estimation (GAE) with the entropy loss added onto policy loss to encourage
exploration. Once these losses have been calculated, we add them all together, backprop to find all
gradients and then optimise with Adam and we go back to the start of the main training loop.
"""

import torch
import sys

from a3c.task_util import get_model_from_task
from gym_ai2thor.envs.mcs_env import McsEnv
from point_goal_navigation.common.utils import batch_obs, set_random_object_goal
from a3c.task_util import check_gpu_usage_and_restart_env


def ensure_shared_grads(model, shared_model):
    for param, shared_param in zip(model.parameters(),
                                   shared_model.parameters()):
        if shared_param.grad is not None:
            return
        shared_param._grad = param.grad


def train(rank, args, shared_model, counter, lock, optimizer):
    torch.manual_seed(args.seed + rank)

    env = McsEnv(seed=args.seed + rank)
    nav_env, navigator, model = get_model_from_task(env, args.task)
    nav_env.reset(random_init=True)
    set_random_object_goal(navigator, env.scene_config)

    model = model.to(args.device)
    model.train()

    state = navigator.get_observation(nav_env.step_output)
    done = True

    # monitoring
    total_reward_for_num_steps_list = []
    episode_total_rewards_list = []
    avg_reward_for_num_steps_list = []

    total_length = 0
    episode_length = 0
    n_episode = 0
    all_rewards_in_episode = []
    while True:
        # Sync with the shared model

        model.load_state_dict(shared_model.state_dict())

        done_mask = torch.zeros(size=(1,1)).to(args.device)
        undone_mask = torch.ones(size=(1,1)).to(args.device)

        if done:
            rnn_hidden_states = torch.zeros(size=(model.net.num_recurrent_layers, 1, 512)).to(args.device)
            prev_action = torch.zeros(1, 1).to(args.device)
            mask = done_mask
        else:
            rnn_hidden_states = rnn_hidden_states.detach()

        values = []
        log_probs = []
        rewards = []
        entropies = []

        for step in range(args.num_steps):
            episode_length += 1
            total_length += 1

            batch = batch_obs(state, args.device)
            value, action, action_log_probs, rnn_hidden_states = model.act(batch, rnn_hidden_states, prev_action, mask)
            # torch.cuda.empty_cache()

            prev_action.copy_(action)
            mask = undone_mask

            entropies.append(-action_log_probs * torch.exp(action_log_probs))
            log_probs.append(action_log_probs)

            action_int = action.cpu().numpy()[0][0].item()

            reward, done = navigator.navigation_step_with_reward(nav_env, action_int)
            state = navigator.get_observation(nav_env.step_output)
            done = done or episode_length >= args.max_episode_length

            values.append(value)
            rewards.append(reward)
            all_rewards_in_episode.append(reward)

            with lock:
                counter.value += 1

            if done:
                total_length -= 1
                total_reward_for_episode = sum(all_rewards_in_episode)
                episode_total_rewards_list.append(total_reward_for_episode)
                all_rewards_in_episode = []
                episode_success = (reward == 9.99)
                print('Process {} Episode {} Over with Length: {} and Reward: {: .2f}, Success: {}. Total Trained Length: {}'.format(
                    rank, n_episode, episode_length, total_reward_for_episode, episode_success, total_length))

                # if args.device != "cpu:":
                #     env, nav_env = check_gpu_usage_and_restart_env(env, nav_env)
                if episode_success:
                    nav_env.reset(random_init=True)
                else:
                    nav_env.reset(repeat_current=True)
                set_random_object_goal(navigator, env.scene_config)
                state = navigator.get_observation(nav_env.step_output)
                sys.stdout.flush()
                episode_length = 0
                n_episode += 1
                break


        total_reward_for_num_steps = sum(rewards)
        total_reward_for_num_steps_list.append(total_reward_for_num_steps)
        avg_reward_for_num_steps = total_reward_for_num_steps / len(rewards)
        avg_reward_for_num_steps_list.append(avg_reward_for_num_steps)

        # Backprop and optimisation
        R = torch.zeros(1, 1).to(args.device)
        gae = torch.zeros(1, 1).to(args.device)
        batch = batch_obs(state, args.device)

        if not done:  # to change last reward to predicted value to ....
            value, _, _, _ = model.act(batch, rnn_hidden_states, prev_action, mask)
            R = value.detach()

        values.append(R)
        policy_loss = 0
        value_loss = 0
        # import pdb;pdb.set_trace() # good place to breakpoint to see training cycle

        for i in reversed(range(len(rewards))):
            R = args.gamma * R + rewards[i]
            advantage = R - values[i]
            value_loss = value_loss + 0.5 * advantage.pow(2)

            # Generalized Advantage Estimation
            delta_t = rewards[i] + args.gamma * values[i + 1] - values[i]
            gae = gae * args.gamma * args.tau + delta_t

            policy_loss = policy_loss - log_probs[i] * gae.detach() - \
                          args.entropy_coef * entropies[i]

        optimizer.zero_grad()

        (policy_loss + args.value_loss_coef * value_loss).backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), args.max_grad_norm)

        ensure_shared_grads(model, shared_model)
        optimizer.step()

