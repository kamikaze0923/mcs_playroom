import numpy as np
from PIL import Image

from torch.utils.data import Dataset
import torch
import os

np.random.seed(0)

class Objects(Dataset):
    def __init__(self):
        sphere_tensor = torch.load(os.path.join("appearance", "object_mask_frame", "sphere", "0.pth"))
        cube_tensor = torch.load(os.path.join("appearance", "object_mask_frame", "cube", "0.pth"))
        sphere_target = torch.zeros(size=(sphere_tensor.size()[0],))
        cube_target = torch.ones(size=(cube_tensor.size()[0],))
        self.data = torch.cat([sphere_tensor, cube_tensor])
        self.targets = torch.cat([sphere_target, cube_target])

    def __getitem__(self, index):
        return (self.data[index], self.targets[index])

    def __len__(self):
        return self.data.size()[0]


class TripletObjects(Dataset):
    """
    Train: For each sample (anchor) randomly chooses a positive and negative samples
    Test: Creates fixed triplets for testing
    """

    def __init__(self, object_dataset):
        self.object_dataset = object_dataset
        self.transform = None

        self.train_labels = self.object_dataset.targets
        self.train_data = self.object_dataset.data
        self.labels_set = set(self.train_labels.numpy())
        self.label_to_indices = {label: np.where(self.train_labels.numpy() == label)[0] for label in self.labels_set}


    def __getitem__(self, index):
        img1, label1 = self.train_data[index], self.train_labels[index].item()
        positive_index = index
        while positive_index == index:
            positive_index = np.random.choice(self.label_to_indices[label1])
        negative_label = np.random.choice(list(self.labels_set - set([label1])))
        negative_index = np.random.choice(self.label_to_indices[negative_label])
        img2 = self.train_data[positive_index]
        img3 = self.train_data[negative_index]

        return (img1, img2, img3), []

    def __len__(self):
        return len(self.object_dataset)

