from locomotion.datasets import get_train_test_dataset
from locomotion.network import Position_Embbedding_Network, HIDDEN_STATE_SIZE
from locomotion.train import MODEL_SAVE_DIR, TRAIN_BATCH_SIZE, TEST_BATCH_SIZE
from torch.utils.data.dataloader import DataLoader
import numpy as np
import torch
import os
import matplotlib.pyplot as plt


LOCOMOTION_FIGURE_DIR = os.path.join("locomotion", "figure")


def get_hidden_state_embedding(dataloader, net, batch_size):
    with_occluder_prediction = []
    without_occluder_target = []
    for _, (with_occluder, without_occluder) in enumerate(dataloader):
        h_0 = torch.zeros(
            size=(1, batch_size, HIDDEN_STATE_SIZE))  # (num_layer, batch_size, hidden_size)

        input_1 = (with_occluder, h_0)
        output_1, _ = net(input_1)
        with_occluder_prediction.append(output_1)

        without_occluder_target.append(without_occluder[:,:,[0,1]])

    with_occluder_emb = torch.cat(with_occluder_prediction)
    without_occluder_emb = torch.cat(without_occluder_target)
    return with_occluder_emb.detach().numpy(), without_occluder_emb.detach().numpy()



def get_embedding():
    train_set, test_set = get_train_test_dataset()
    assert len(train_set) % TRAIN_BATCH_SIZE == 0, len(test_set) % TEST_BATCH_SIZE == 0
    train_loader = DataLoader(dataset=train_set, batch_size=TRAIN_BATCH_SIZE, shuffle=True)
    test_loader = DataLoader(dataset=test_set, batch_size=TEST_BATCH_SIZE, shuffle=False)

    net = Position_Embbedding_Network()
    net.eval()
    net.load_state_dict(torch.load(os.path.join(MODEL_SAVE_DIR, "model_{}_hidden_state.pth".format(HIDDEN_STATE_SIZE))))

    train_emb = get_hidden_state_embedding(train_loader, net, TRAIN_BATCH_SIZE)
    test_emb = get_hidden_state_embedding(test_loader, net, TEST_BATCH_SIZE)

    return train_emb, test_emb


def plot():
    _, test_emb = get_embedding()
    test_emb_with_occluder, test_emb_without_occluder = test_emb
    print(test_emb_with_occluder.shape, test_emb_without_occluder.shape)
    assert test_emb_with_occluder.shape[0] == test_emb_without_occluder.shape[0]

    os.makedirs(LOCOMOTION_FIGURE_DIR, exist_ok=True)

    for i in range(test_emb_with_occluder.shape[0]):
        plt.title("Latent State(2D) Trajectory of Object {} Locomotion".format(i))
        x = test_emb_with_occluder[i, :, 0]
        y = test_emb_with_occluder[i, :, 1]
        plt.scatter(x, y, s=0.5, label="With Occulder")
        x = test_emb_without_occluder[i, :, 0]
        y = test_emb_without_occluder[i, :, 1]
        plt.scatter(x, y, s=0.5, label="Without Occulder")
        plt.legend()
        plt.savefig(os.path.join(LOCOMOTION_FIGURE_DIR, "{}.png".format(i)))
        plt.close()
    exit(0)




if __name__ == "__main__":
    plot()