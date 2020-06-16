from torch.nn.modules import Module
import torch

HIDDEN_STATE_SIZE = 32
OUTPUT_STATE_SIZE = 2



class Position_Embbedding_Network(Module):
    def __init__(self):
        super().__init__()
        self.gru_1 = torch.nn.GRU(input_size=28, hidden_size=HIDDEN_STATE_SIZE, num_layers=1, batch_first=True)
        self.fc = torch.nn.Linear(in_features=HIDDEN_STATE_SIZE, out_features=OUTPUT_STATE_SIZE)


    def forward(self, input):
        x, h_0 = input
        output, h_0 = self.gru_1(x, h_0)
        output = self.fc(output)
        return output, h_0


if __name__ == "__main__":
    net = Position_Embbedding_Network()

