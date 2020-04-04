
import torch.nn as nn
import torch.distributions
from typing import List, Dict, Optional
from collections import defaultdict
import numpy as np
import quaternion


class Flatten(nn.Module):
    def forward(self, x):
        return x.view(x.size(0), -1)


class CustomFixedCategorical(torch.distributions.Categorical):
    def sample(self, sample_shape=torch.Size()):
        return super().sample(sample_shape).unsqueeze(-1)

    def log_probs(self, actions):
        return (
            super()
            .log_prob(actions.squeeze(-1))
            .view(actions.size(0), -1)
            .sum(-1)
            .unsqueeze(-1)
        )

    def mode(self):
        return self.probs.argmax(dim=-1, keepdim=True)


class CategoricalNet(nn.Module):
    def __init__(self, num_inputs, num_outputs):
        super().__init__()

        self.linear = nn.Linear(num_inputs, num_outputs)

        nn.init.orthogonal_(self.linear.weight, gain=0.01)
        nn.init.constant_(self.linear.bias, 0)

    def forward(self, x):
        x = self.linear(x)
        return CustomFixedCategorical(logits=x)


def _to_tensor(v):
    if torch.is_tensor(v):
        return v
    elif isinstance(v, np.ndarray):
        return torch.from_numpy(v)
    else:
        return torch.tensor(v, dtype=torch.float)


def batch_obs(
    observations: List[Dict], device: Optional[torch.device] = None
) -> Dict[str, torch.Tensor]:
    r"""Transpose a batch of observation dicts to a dict of batched
    observations.

    Args:
        observations:  list of dicts of observations.
        device: The torch.device to put the resulting tensors on.
            Will not move the tensors if None

    Returns:
        transposed dict of lists of observations.
    """
    batch = defaultdict(list)

    for obs in observations:
        for sensor in obs:
            batch[sensor].append(_to_tensor(obs[sensor]))

    for sensor in batch:
        batch[sensor] = (
            torch.stack(batch[sensor], dim=0)
            .to(device=device)
            .to(dtype=torch.float)
        )

    return batch


def normalize_3d_rotation(delta_x, delta_z):
    if delta_x == 0 and delta_z ==0:
        return 0, 0
    norm = (delta_x ** 2 + delta_z ** 2) ** 0.5
    return delta_x / norm, delta_z / norm

def quaternion_rotate_vector(quat, v):
    vq = np.quaternion(0, 0, 0, 0)
    vq.imag = v
    return (quat * vq * quat.inverse()).imag

def quat_from_angle_axis(theta, axis=np.array([0,1,0])):
    axis = axis.astype(np.float)
    axis /= np.linalg.norm(axis)
    return quaternion.from_rotation_vector(theta * axis)






