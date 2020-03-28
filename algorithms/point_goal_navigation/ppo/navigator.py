
from algorithms.point_goal_navigation.ppo.policy import PointNavBaselinePolicy
import torch
from collections import OrderedDict


class Navigator:


    def __init__(self, observation_space, action_space, goal_sensor_uuid):
        self.actor_critic = PointNavBaselinePolicy(
            observation_space,
            action_space,
            goal_sensor_uuid
        )


    def load_checkpoint(self, checkpoint_path):
        state_dict = torch.load(checkpoint_path, map_location='cpu')
        state_dict = rename_state_dict_keys(state_dict, key_transformation_funtion)
        self.actor_critic.load_state_dict(state_dict['state_dict'])

def key_transformation_funtion(old_key):
    transform = {
        "actor_critic.net.rnn.weight_ih_l0": "net.state_encoder.rnn.weight_ih_l0",
        "actor_critic.net.rnn.weight_hh_l0": "net.state_encoder.rnn.weight_hh_l0",
        "actor_critic.net.rnn.bias_ih_l0": "net.state_encoder.rnn.bias_ih_l0",
        "actor_critic.net.rnn.bias_hh_l0": "net.state_encoder.rnn.bias_hh_l0",

        "actor_critic.net.critic_linear.weight": "critic.fc.weight",
        "actor_critic.net.critic_linear.bias": "critic.fc.bias",
        "actor_critic.action_distribution.linear.weight": "action_distribution.linear.weight",
        "actor_critic.action_distribution.linear.bias": "action_distribution.linear.bias",
    }
    if old_key in transform:
        return transform[old_key]
    return old_key


def rename_state_dict_keys(old_dict, key_transformation):
    new_state_dict = OrderedDict()
    for key, value in old_dict['state_dict'].items():
        new_key = key_transformation(key)
        new_state_dict[new_key] = value
    old_dict['state_dict'] = new_state_dict
    return old_dict



