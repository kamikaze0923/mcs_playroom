from torch.nn.modules import Module
import torch

HIDDEN_STATE_SIZE = 24
POSITION_TRACK_DIM = 2

POSITION_FEATURE_DIM = 29

CUDA = torch.cuda.is_available()
if CUDA:
    print("Use GPU")

class ObjectStatePrediction(Module):
    def __init__(self):
        super().__init__()
        self.gru_1 = torch.nn.GRU(input_size=POSITION_FEATURE_DIM, hidden_size=HIDDEN_STATE_SIZE, num_layers=1, batch_first=True)
        self.position_fc = torch.nn.Linear(in_features=HIDDEN_STATE_SIZE, out_features=POSITION_TRACK_DIM)
        self.leave_scene_fc = torch.nn.Linear(in_features=HIDDEN_STATE_SIZE, out_features=1)
        if CUDA:
            self.cuda()

    def forward(self, input):
        x, h_t = input
        print(x.device)
        print(h_t.device)
        exit(0)
        hidden_state, h_t = self.gru_1(x, h_t)
        position_pred = self.position_fc(hidden_state)
        leave_scene_pred = torch.sigmoid(self.leave_scene_fc(hidden_state).squeeze())
        return (position_pred, leave_scene_pred), h_t


if __name__ == "__main__":
    net = ObjectStatePrediction()

