from torch.nn.modules import Module
import torch
import sys

HIDDEN_STATE_SIZE = int(sys.argv[1])
NUM_HIDDEN_LAYER = 1
print("LSTM Hidden State Size: {}".format(HIDDEN_STATE_SIZE))
print("LSTM Hidden Layer Size: {}".format(NUM_HIDDEN_LAYER))

POSITION_FEATURE_DIM = 30
POSITION_TRACK_DIM = 2

class ObjectStatePrediction(Module):
    def __init__(self):
        super().__init__()
        self.lstm = torch.nn.LSTM(
            input_size=POSITION_FEATURE_DIM, hidden_size=HIDDEN_STATE_SIZE, num_layers=NUM_HIDDEN_LAYER, batch_first=True
        )
        self.all_fc = torch.nn.Linear(in_features=HIDDEN_STATE_SIZE, out_features=HIDDEN_STATE_SIZE)
        self.position_fc = torch.nn.Linear(in_features=HIDDEN_STATE_SIZE, out_features=POSITION_TRACK_DIM)
        self.leave_scene_fc = torch.nn.Linear(in_features=HIDDEN_STATE_SIZE, out_features=1)
        self.drop_out = torch.nn.Dropout(0.5)


    def forward(self, input):
        x, h_t, c_t = input
        hidden_states, (h_t, c_t) = self.lstm(x, (h_t, c_t))
        fc_hidden_states = torch.relu(self.all_fc(hidden_states))
        position_pred = self.position_fc(fc_hidden_states)
        leave_scene_pred = torch.sigmoid(self.leave_scene_fc(hidden_states).squeeze())
        return (position_pred, leave_scene_pred), (h_t, c_t)


if __name__ == "__main__":
    net = ObjectStatePrediction()

