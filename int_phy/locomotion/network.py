from torch.nn.modules import Module
from int_phy.locomotion.datasets import DEVICE
import torch

HIDDEN_STATE_SIZE = 32
NUM_HIDDEN_LAYER = 1
print("LSTM Hidden State Size: {}".format(HIDDEN_STATE_SIZE))
print("LSTM Hidden Layer Size: {}".format(NUM_HIDDEN_LAYER))

POSITION_FEATURE_DIM = 30
POSITION_TRACK_DIM = 2
OBJECT_IN_SCENE_BIT = -1

class ObjectStatePrediction(Module):
    def __init__(self):
        super().__init__()
        # self.lstm = torch.nn.LSTM(
        #     input_size=POSITION_FEATURE_DIM, hidden_size=HIDDEN_STATE_SIZE, num_layers=NUM_HIDDEN_LAYER, batch_first=True
        # )
        self.lstm_cell = torch.nn.LSTMCell(input_size=POSITION_FEATURE_DIM, hidden_size=HIDDEN_STATE_SIZE)
        self.all_fc = torch.nn.Linear(in_features=HIDDEN_STATE_SIZE, out_features=HIDDEN_STATE_SIZE)
        self.position_fc = torch.nn.Linear(in_features=HIDDEN_STATE_SIZE, out_features=POSITION_TRACK_DIM)
        self.leave_scene_fc = torch.nn.Linear(in_features=HIDDEN_STATE_SIZE, out_features=1)
        self.drop_out = torch.nn.Dropout(0.5)

    def custumiszed_lstm_cell_forward(
            self, x, hidden_states, invalid_output = torch.zeros(size=(1, HIDDEN_STATE_SIZE)).to(DEVICE)
    ):
        h_t, c_t = hidden_states
        assert h_t.size()[0] == c_t.size()[0]

        output_h_t = []
        every_layer_final_h_t = [[] for _ in range(NUM_HIDDEN_LAYER)]
        every_layer_final_c_t = [[] for _ in range(NUM_HIDDEN_LAYER)]
        for i, x_one_seq in enumerate(x):
            for j in range(NUM_HIDDEN_LAYER):
                h_t_one, c_t_one = h_t[j][i].unsqueeze(0), c_t[j][i].unsqueeze(0)
                one_layer_h_t = []
                final_h_t, final_c_t = h_t_one, c_t_one
                for k, x_one in enumerate(x_one_seq):
                    if x_one[OBJECT_IN_SCENE_BIT] == 1:
                        # print("valid step: {}".format(k))
                        h_t_one, c_t_one = self.lstm_cell(x_one.unsqueeze(0), (h_t_one, c_t_one))
                        one_layer_h_t.append(h_t_one)
                        final_h_t = h_t_one
                        final_c_t = c_t_one
                    else:
                        # print("int valid step: {}".format(k))
                        one_layer_h_t.append(invalid_output)
                every_layer_final_h_t[j].append(final_h_t)
                every_layer_final_c_t[j].append(final_c_t)
                one_layer_h_t = torch.cat(one_layer_h_t, dim=0)
                x_one_seq = one_layer_h_t.clone()
            output_h_t.append(one_layer_h_t)

        for j in range(NUM_HIDDEN_LAYER):
            every_layer_final_h_t[j] = torch.cat(every_layer_final_h_t[j])
            every_layer_final_c_t[j] = torch.cat(every_layer_final_c_t[j])

        output_h_t = torch.stack(output_h_t, dim=0)
        every_layer_final_h_t = torch.stack(every_layer_final_h_t)
        every_layer_final_c_t = torch.stack(every_layer_final_c_t)
        return output_h_t, (every_layer_final_h_t, every_layer_final_c_t)

    def forward(self, input):
        x, h_t, c_t = input
        hidden_states, (h_t, c_t) = self.lstm(x, (h_t, c_t))
        hidden_states, (h_t, c_t) = self.custumiszed_lstm_cell_forward(x, (h_t, c_t))
        # fc_hidden_states = torch.relu(self.all_fc(hidden_states))
        position_pred = self.position_fc(fc_hidden_states)
        leave_scene_pred = torch.sigmoid(self.leave_scene_fc(hidden_states))
        return (position_pred, leave_scene_pred), (h_t, c_t)


if __name__ == "__main__":
    net = ObjectStatePrediction()

