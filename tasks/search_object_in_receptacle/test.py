"""
Adapted from https://github.com/ikostrikov/pytorch-a3c/blob/master/test.py

Contains the testing loop of the shared model within A3C (no optimisation/backprop needed)
Usually this is run concurrently while training occurs and is useful for tracking progress. But to
save resources we can choose to only test every args.test_sleep_time seconds.
"""

import time

import torch

from a3c.task_util import get_model_from_task
from gym_ai2thor.envs.mcs_env import McsEnv
from tasks.search_object_in_receptacle.utils import set_object_goal
from gym_ai2thor.utils import CSVLogger
from metaController.meta_controller import MetaController
from a3c.task_util import check_gpu_usage_and_restart_env

import os
from copy import deepcopy
from a3c.common import batch_obs

def test(rank, args, shared_model, counter):
    torch.manual_seed(args.seed + rank)
    env = McsEnv(seed=args.seed + rank, task="interaction_scenes", scene_type="traversal")
    face_env, faceTurner, model, _, _ = get_model_from_task(env, args.task)
    face_env.reset(random_init=True)

    metaController = MetaController(env)
    metaController.get_inital_planner_state()
    metaController.excecute()
    set_object_goal(faceTurner, env.scene_config)

    model = model.to(args.device)
    model.eval()

    state = faceTurner.get_observation(face_env.step_output)
    reward_sum = 0
    done = True

    save = 'steps{}-process{}-lr{}-entropy_coef{}-max_grad_norm{}'.format(args.num_steps, args.num_processes,
                                                             args.lr, args.entropy_coef, args.max_grad_norm)
    save = os.path.join('logs', save)
    os.makedirs(save, exist_ok=True)


    logger = CSVLogger(os.path.join(save, 'test.csv'))
    fileds = ['episode_success_rate', 'frames_rendered']
    logger.log(fileds)

    start_time = time.time()

    episode_length = 0
    ckpt_counter = 0
    n_test_episode = 40
    while True:
        success_cnt = 0
        for _ in range(n_test_episode):
            while True:
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
                reward, done = faceTurner.object_search_step_with_reward(
                    face_env, action_int, episode_length >= args.max_episode_length
                )
                state = faceTurner.get_observation(face_env.step_output)
                reward_sum += reward

                if done:
                    episode_success = (reward == 0.99)
                    if episode_success:
                        success_cnt += 1
                    print(
                        "Time {}, num steps over all threads {}, FPS {:.0f}, episode reward {: .3f}, success {}, episode length {}".format(
                        time.strftime("%Hh %Mm %Ss", time.gmtime(time.time() - start_time)),
                        counter.value, counter.value / (time.time() - start_time),
                        reward_sum, episode_success, episode_length)
                    )
                    # if args.device != "cpu:":
                    #     env, nav_env = check_gpu_usage_and_restart_env(env, nav_env)

                    reward_sum = 0
                    episode_length = 0
                    face_env.reset(random_init=True)
                    set_object_goal(faceTurner, env.scene_config)
                    metaController.get_inital_planner_state()
                    metaController.excecute()
                    state = faceTurner.get_observation(face_env.step_output)
                    break

        torch.save(model.state_dict(), os.path.join(save, "ckpt{}.pth".format(ckpt_counter)))
        logger.log(["{: .2f}".format(success_cnt / n_test_episode), counter.value])
        time.sleep(args.test_sleep_time)
        ckpt_counter += 1
        if ckpt_counter == 48 * 2:
            env.controller.end_scene(None, None)
            logger.close()
            break


