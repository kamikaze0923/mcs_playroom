from torch.utils.data import Dataset
import torch
import os

# N_TRAIN = 6400
# N_TEST = 1200

N_TRAIN = 75
N_TEST = 75


SCENE_TYPES = ["object_permanence", "shape_constancy", "spatio_temporal_continuity"]
SHAPE_TYPES = ["cylinder", "sphere", "cube"]
DATA_SAVE_DIR = os.path.join("int_phy", "locomotion", "positions_old_additional")

torch.set_printoptions(profile="full", precision=2, linewidth=10000)

if torch.cuda.is_available():
    DEVICE = "cuda:0"
else:
    DEVICE = "cpu"

print("Uing {}".format(DEVICE))

def load_all_tensors(occluder_dir):
    occluder_tensor = []
    for t in SHAPE_TYPES:
        shape_dir = os.path.join(DATA_SAVE_DIR, occluder_dir, t)
        for scene_dir in SCENE_TYPES:
            scene_dir = os.path.join(shape_dir, scene_dir)
            tensor_files = os.listdir(scene_dir)
            for file in tensor_files:
                file = os.path.join(scene_dir, file)
                # print(file)
                tensor = torch.load(file)
                tensor = tensor[torch.sum(tensor[:,:,-1], dim=1) != 0]
                # in case some in gravity scene the obj does not appear at all
                occluder_tensor.append(tensor)
    return occluder_tensor


def get_train_test_dataset():
    with_occluder_tensor = torch.cat(load_all_tensors("with_occluder")).to(DEVICE)
    without_occluder_tensor = torch.cat(load_all_tensors("without_occluder")).to(DEVICE)
    assert with_occluder_tensor.size() == without_occluder_tensor.size()
    rand_permutation = torch.randperm(with_occluder_tensor.size()[0])
    without_occluder_tensor = without_occluder_tensor[rand_permutation]
    with_occluder_tensor = with_occluder_tensor[rand_permutation]
    train_set = TuplePositions(with_occluder_tensor[:N_TRAIN], without_occluder_tensor[:N_TRAIN])
    # test_set = TuplePositions(with_occluder_tensor[N_TRAIN:], without_occluder_tensor[N_TRAIN:])
    test_set = TuplePositions(with_occluder_tensor[:N_TRAIN], without_occluder_tensor[:N_TRAIN])
    assert len(train_set) == N_TRAIN
    assert len(test_set) == N_TEST
    return train_set, test_set


class TuplePositions(Dataset):
    def __init__(self, with_occluder, without_occluder):
        self.with_occluder_tensor = with_occluder
        self.without_occluder_tensor = without_occluder
        print(self.with_occluder_tensor.size(), self.without_occluder_tensor.size())
        assert self.with_occluder_tensor.size() == self.without_occluder_tensor.size()

    def __getitem__(self, index):
        return (self.with_occluder_tensor[index], self.without_occluder_tensor[index])

    def __len__(self):
        return self.with_occluder_tensor.size()[0]



if __name__ == "__main__":
    dataset = get_train_test_dataset()
