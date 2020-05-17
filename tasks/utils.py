import torch


def get_goal_embedding(observations, goal_sensor_uuid, object_encoder=None):
    goal_observations = observations[goal_sensor_uuid]
    if goal_sensor_uuid == "pointgoal_with_gps_compass":
        goal_observations = torch.stack(
            [
                goal_observations[:, 0],
                torch.cos(-goal_observations[:, 1]),
                torch.sin(-goal_observations[:, 1]),
            ],
            -1,
        )
    elif goal_sensor_uuid == "goal_object_information":
        assert object_encoder
        goal_observations = object_encoder(goal_observations)
    return goal_observations

def get_goal_embedding_dimension(goal_sensor_uuid):
    if goal_sensor_uuid == "pointgoal_with_gps_compass":
        return 3
    elif goal_sensor_uuid == "goal_object_information":
        return 32