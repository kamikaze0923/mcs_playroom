import torch
from appearance.datasets import Objects
from appearance.utils import cuda, plot_embeddings, extract_embeddings, get_multivariate_gaussion_parameters
from appearance.networks import EmbeddingNet, TripletNet
import os
import numpy as np

embedding_net = EmbeddingNet()
model = TripletNet(embedding_net)
model.embedding_net.load_state_dict(torch.load(os.path.join("appearance", "pre_trained", "model.pth")))

batch_size = 48
train_dataset = Objects()
kwargs = {'num_workers': 1, 'pin_memory': True} if cuda else {}
train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True, **kwargs)

train_embeddings_tl, train_labels_tl = extract_embeddings(train_loader, model)
para = get_multivariate_gaussion_parameters(train_embeddings_tl, train_labels_tl)
plot_embeddings(train_embeddings_tl, train_labels_tl)

para_dict = {}
for i, (mean, cov) in enumerate(para):
    para_dict['object_{}_mean'.format(i)] = torch.tensor(mean)
    para_dict['object_{}_cov'.format(i)] = torch.tensor(cov)

torch.save(para_dict, os.path.join("appearance", "pre_trained", "embedding_distribution.pth"))

