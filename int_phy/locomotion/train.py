from int_phy.locomotion.datasets import get_train_test_dataset, DEVICE
from int_phy.locomotion.network import ObjectStatePrediction, HIDDEN_STATE_SIZE, NUM_HIDDEN_LAYER, OBJECT_IN_SCENE_BIT
from torch.optim import Adam
from torch.optim import lr_scheduler
from torch.utils.data.dataloader import DataLoader
from torch.nn import MSELoss, BCELoss
import torch
import os
import matplotlib.pyplot as plt
import numpy as np

# TRAIN_BATCH_SIZE = 200
# TEST_BATCH_SIZE = 300

TRAIN_BATCH_SIZE = 200
TEST_BATCH_SIZE = 3756


N_EPOCH = 20000
CHECK_LOSS_INTERVAL = 1
assert N_EPOCH % CHECK_LOSS_INTERVAL == 0

mse = MSELoss(reduction='none')
bce = BCELoss(reduction='none')

torch.set_printoptions(profile="full", precision=2, linewidth=10000)
torch.manual_seed(10)

MODEL_SAVE_DIR = os.path.join("int_phy", "locomotion", "pre_trained_old")

def set_loss(dataloader, net):
    total_loss = 0
    h_0 = torch.zeros(size=(NUM_HIDDEN_LAYER, dataloader.batch_size, HIDDEN_STATE_SIZE)).to(DEVICE)  # (num_layer, batch_size, hidden_size)
    c_0 = torch.zeros(size=(NUM_HIDDEN_LAYER, dataloader.batch_size, HIDDEN_STATE_SIZE)).to(DEVICE)  # (num_layer, batch_size, hidden_size)
    for with_occluder, without_occluder in dataloader:

        input_1 = (with_occluder,h_0, c_0)
        output_1, _ = net(input_1)

        final_loss = batch_final_loss(output_1, without_occluder, dataloader.batch_size)

        total_loss += final_loss.item()
    total_loss /= len(dataloader)
    return total_loss


def batch_final_loss(output, ground_truth, batch_size, print_info=False):
    position_pred, leave_scene_pred = output

    position_used = ground_truth[:, :, [0, 1]]

    # Only measure position loss for in scene objects, otherwise (0,0) makes no sense
    valid_ground_truth = ground_truth[:, :, OBJECT_IN_SCENE_BIT] == 1
    position_pred = position_pred[valid_ground_truth]
    position_target = create_position_target(position_used, valid_ground_truth)
    leave_scene_pred = leave_scene_pred[valid_ground_truth].squeeze()
    leave_scene_target = create_leave_scene_target(valid_ground_truth)

    mse_loss_weight, bce_loss_weight = get_batch_loss_weight(valid_ground_truth)
    position_loss = weighted_mse(position_pred, position_target, mse_loss_weight)
    leave_scene_loss = weighted_bce(leave_scene_pred, leave_scene_target, bce_loss_weight)

    final_loss = (torch.sum(position_loss) + torch.sum(leave_scene_loss)) / batch_size
    if print_info:
        leave_scene_pred_numpy = leave_scene_pred[leave_scene_target == 1].detach().cpu().numpy()
        print(
            "When object leave scene, the average predict probability is {:.2f} +- {:.2f}".format(
                np.mean(leave_scene_pred_numpy), np.std(leave_scene_pred_numpy)
            )
        )
        position_loss_numpy = position_loss.detach().cpu().numpy()
        print("Position mse error {:.4f} +- {:.4f}".format(
            np.mean(position_loss_numpy), np.std(position_loss_numpy))
        )

    return final_loss


def weighted_mse(pred, target, weight):
    loss = mse(pred, target)
    loss = torch.sum(loss, dim=1)
    return loss * weight


def weighted_bce(pred, target, weight):
    loss = bce(pred, target)
    return loss * weight

def get_batch_loss_weight(valid_ground_truth):
    bce_n_loss = torch.sum(valid_ground_truth, dim=1)
    bce_loss_weight = 1 / bce_n_loss.detach().clone().float()
    bce_loss_weight = torch.repeat_interleave(bce_loss_weight, bce_n_loss)

    mse_n_loss = bce_n_loss - 1
    mse_loss_weight = 1 / mse_n_loss.detach().clone().float()
    mse_loss_weight = torch.repeat_interleave(mse_loss_weight, bce_n_loss)
    mse_loss_weight[torch.cumsum(bce_n_loss, dim=0) - 1] = 0

    return mse_loss_weight, bce_loss_weight

def create_leave_scene_target(valid_ground_truth):
    n_steps = torch.sum(valid_ground_truth, dim=1)
    leave_scene_step = torch.cumsum(n_steps, dim=0) - 1
    total_batch_step = torch.sum(n_steps).item()
    target = torch.zeros(size=(total_batch_step,)).to(DEVICE)
    target[leave_scene_step] = 1
    return target

def create_position_target(position_used, valid_ground_truth): # move ground truth forward 1 step
    batch_size, step_len = valid_ground_truth.size()

    valid_ground_truth_expanded = torch.cat([valid_ground_truth, torch.zeros(size=(batch_size, 1)).bool().to(DEVICE)], dim=1)
    # print(valid_ground_truth[0])
    # print(valid_ground_truth_expanded[0])

    all_steps = torch.arange(0, step_len+1).repeat(batch_size, 1).to(DEVICE)
    scene_steps = torch.mul(valid_ground_truth_expanded.float(), all_steps)

    last_scene_step_next = torch.argmax(scene_steps, dim=1) + 1
    valid_ground_truth_expanded[torch.arange(0, batch_size), last_scene_step_next] = True

    scene_steps[scene_steps == 0] = 99 # change 0 to some number > 60, use argmin to find the first step
    first_scene_step = torch.argmin(scene_steps, dim=1)
    valid_ground_truth_expanded[torch.arange(0, batch_size), first_scene_step] = False

    position_used_expand = torch.cat([position_used, torch.zeros(size=(batch_size, 1, 2)).to(DEVICE)], dim=1)

    return position_used_expand[valid_ground_truth_expanded]


def train():
    train_set, test_set = get_train_test_dataset()
    assert len(train_set) % TRAIN_BATCH_SIZE == 0
    assert len(test_set) % TEST_BATCH_SIZE == 0
    train_loader = DataLoader(dataset=train_set, batch_size=TRAIN_BATCH_SIZE, shuffle=True)
    test_loader = DataLoader(dataset=test_set, batch_size=TEST_BATCH_SIZE, shuffle=False)

    net = ObjectStatePrediction().to(DEVICE)
    net.load_state_dict(
        torch.load(
            os.path.join(
                MODEL_SAVE_DIR, "model_{}_hidden_state.pth".format(HIDDEN_STATE_SIZE)
            )
        )
    )

    optimizer = Adam(params=net.parameters(), lr=1e-3)
    scheduler = lr_scheduler.StepLR(optimizer, step_size=1000, gamma=0.9, last_epoch=-1)

    all_train_loss = []
    all_test_loss = []

    h_0 = torch.zeros(size=(NUM_HIDDEN_LAYER, TRAIN_BATCH_SIZE, HIDDEN_STATE_SIZE)).to(DEVICE) # (num_layer, batch_size, hidden_size)
    c_0 = torch.zeros(size=(NUM_HIDDEN_LAYER, TRAIN_BATCH_SIZE, HIDDEN_STATE_SIZE)).to(DEVICE)  # (num_layer, batch_size, hidden_size)
    os.makedirs(MODEL_SAVE_DIR, exist_ok=True)
    best_loss = float('inf')
    best_epoch = None
    for epoch in range(N_EPOCH):
        net.train()
        for _, (with_occluder, without_occluder) in enumerate(train_loader):

            input_1 = (with_occluder, h_0, c_0)
            output_1, _ = net(input_1)

            final_loss = batch_final_loss(output_1, without_occluder, train_loader.batch_size)

            optimizer.zero_grad()
            final_loss.backward()
            optimizer.step()

        if epoch % CHECK_LOSS_INTERVAL == 0:
            print("Epoch {}: Lr {}".format(epoch, scheduler.get_last_lr()))
            net.eval()

            train_loss = set_loss(train_loader, net)
            print("Training    Set Loss {: .15f}".format(train_loss))
            all_train_loss.append(train_loss)

            test_loss = set_loss(test_loader, net)
            print("Validation  Set Loss {: .15f}".format(test_loss))
            all_test_loss.append(test_loss)

            if test_loss < best_loss:
                best_loss = test_loss
                best_epoch = epoch
                torch.save(net.state_dict(), os.path.join(MODEL_SAVE_DIR, "model_{}_hidden_state.pth".format(HIDDEN_STATE_SIZE)))
            print("Best model in epoch {} loss {}".format(best_epoch, best_loss))
        scheduler.step()





    all_epochs = [i*CHECK_LOSS_INTERVAL for i in range(N_EPOCH // CHECK_LOSS_INTERVAL)]
    plt.figure(figsize=(24,6))
    plt.title("Learning Curve")
    plt.plot(all_epochs, all_train_loss, label="Training Set Loss", linewidth=0.4)
    plt.plot(all_epochs, all_test_loss, label="Validation Set Loss", linewidth=0.4)
    plt.legend()
    plt.yscale("log")
    plt.savefig(os.path.join(MODEL_SAVE_DIR, "loss_{}_hidden_state.png".format(HIDDEN_STATE_SIZE)))
    plt.close()








if __name__ == "__main__":
    train()

