from locomotion.datasets import get_train_test_dataset
from locomotion.network import Position_Embbedding_Network, HIDDEN_STATE_SIZE
from torch.optim import Adam
from torch.optim import lr_scheduler
from torch.utils.data.dataloader import DataLoader
import torch
import os
import matplotlib.pyplot as plt

TRAIN_BATCH_SIZE = 40
TEST_BATCH_SIZE = 230
N_EPOCH = 2000

torch.set_printoptions(profile="full", precision=2, linewidth=10000)
torch.manual_seed(5)

MODEL_SAVE_DIR = os.path.join("locomotion", "pre_trained")
OBJECT_IN_SCENE_BIT = -1



def set_loss(dataloader, net):
    total_loss = 0
    for with_occluder, without_occluder in dataloader:
        # print(with_occluder.size(), without_occluder.size())
        h_0 = torch.zeros(size=(1, dataloader.batch_size, HIDDEN_STATE_SIZE))  # (num_layer, batch_size, hidden_size)

        input_1 = (with_occluder,h_0)
        output_1, _ = net(input_1)
        target = without_occluder[:, :, [0, 1]]

        valid_ground_truth = without_occluder[:, :, OBJECT_IN_SCENE_BIT] == 1
        output_1 = output_1[valid_ground_truth]
        target = target[valid_ground_truth]

        loss_weight = get_loss_weight(valid_ground_truth)
        loss = weighted_mse(output_1, target, loss_weight, dataloader.batch_size)
        total_loss += loss.item()
    total_loss /= len(dataloader)
    return total_loss



def weighted_mse(h1, h2, weight, batch_size):
    loss = (h1 - h2) ** 2
    loss = 0.5 * torch.sum(loss, dim=1)
    loss = loss * weight
    return torch.sum(loss) / batch_size

def get_loss_weight(valid_ground_truth):
    n_loss = torch.sum(valid_ground_truth, dim=1)
    loss_weight = 1 / n_loss.detach().clone().float()
    loss_weight = torch.repeat_interleave(loss_weight, n_loss)
    return loss_weight

def train():
    train_set, test_set = get_train_test_dataset()
    assert len(train_set) % TRAIN_BATCH_SIZE == 0, len(test_set) % TEST_BATCH_SIZE == 0
    train_loader = DataLoader(dataset=train_set, batch_size=TRAIN_BATCH_SIZE, shuffle=True)
    test_loader = DataLoader(dataset=test_set, batch_size=TEST_BATCH_SIZE, shuffle=False)

    net = Position_Embbedding_Network()
    optimizer = Adam(params=net.parameters(), lr=1e-3)
    scheduler = lr_scheduler.StepLR(optimizer, step_size=400, gamma=0.5, last_epoch=-1)

    all_train_loss = []
    all_test_loss = []
    for epoch in range(N_EPOCH):
        print("Epoch {}".format(epoch))
        net.train()
        for _, (with_occluder, without_occluder) in enumerate(train_loader):
            h_0 = torch.zeros(size=(1, TRAIN_BATCH_SIZE, HIDDEN_STATE_SIZE))  # (num_layer, batch_size, hidden_size)

            input_1 = (with_occluder, h_0)
            output_1, _ = net(input_1)

            target = without_occluder[:, :, [0,1]]

            # Only measure position loss for in scene objects, otherwise (0,0) makes no sense
            valid_ground_truth = without_occluder[:, :, OBJECT_IN_SCENE_BIT] == 1
            output_1 = output_1[valid_ground_truth]
            target = target[valid_ground_truth]

            loss_weight = get_loss_weight(valid_ground_truth)
            loss = weighted_mse(output_1, target, loss_weight, batch_size=train_loader.batch_size)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        net.eval()
        train_loss = set_loss(train_loader, net)
        print("Training Set Loss {: .15f}".format(train_loss))
        all_train_loss.append(train_loss)

        test_loss = set_loss(test_loader, net)
        print("Testing  Set Loss {: .15f}".format(test_loss))
        all_test_loss.append(test_loss)
        scheduler.step()

    all_epochs = [i for i in range(N_EPOCH)]
    plt.title("Learning Curve")
    plt.plot(all_epochs, all_train_loss, label="Training Loss")
    plt.plot(all_epochs, all_test_loss, label="Testing Loss")
    plt.legend()
    plt.yscale("log")
    plt.savefig(os.path.join(MODEL_SAVE_DIR, "loss_{}_hidden_state.png".format(HIDDEN_STATE_SIZE)))
    plt.close()

    os.makedirs(MODEL_SAVE_DIR, exist_ok=True)
    torch.save(net.state_dict(), os.path.join(MODEL_SAVE_DIR, "model_{}_hidden_state.pth".format(HIDDEN_STATE_SIZE)))






if __name__ == "__main__":
    train()

