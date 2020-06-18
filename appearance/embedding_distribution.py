import torch
from appearance.datasets import Objects
from appearance.train import MODEL_SAVE_DIR
from appearance.utils import cuda, plot_embeddings, extract_embeddings, get_multivariate_gaussion_parameters
from appearance.networks import EmbeddingNet, TripletNet
from int_phy_collect import SHAPE_TYPES

import os

embedding_net = EmbeddingNet()
model = TripletNet(embedding_net)
model.embedding_net.load_state_dict(torch.load(os.path.join(MODEL_SAVE_DIR, "model.pth"), map_location="cpu"))

batch_size = 48
train_dataset = Objects()
kwargs = {'num_workers': 1, 'pin_memory': True} if cuda else {}
train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True, **kwargs)

train_embeddings_tl, train_labels_tl = extract_embeddings(train_loader, model)
para = get_multivariate_gaussion_parameters(train_embeddings_tl, train_labels_tl)
plot_embeddings(train_embeddings_tl, train_labels_tl, os.path.join(MODEL_SAVE_DIR, "embedding.png"))

para_dict = {}
for t, (mean, cov) in zip(SHAPE_TYPES, para):
    para_dict['{}_mean'.format(t)] = torch.tensor(mean)
    para_dict['{}_cov'.format(t)] = torch.tensor(cov)

torch.save(para_dict, os.path.join(MODEL_SAVE_DIR, "embedding_distribution.pth"))

