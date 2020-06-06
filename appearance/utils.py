import matplotlib.pyplot as plt
import numpy as np
import torch

cuda = torch.cuda.is_available()


# mnist_classes = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
# colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
#               '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
#               '#bcbd22', '#17becf']


object_classes = ['Sphere', 'Cube']
colors = ['#1f77b4', '#ff7f0e']



def plot_embeddings(embeddings, targets, xlim=None, ylim=None):
    plt.figure(figsize=(10,10))
    for i in range(2):
        inds = np.where(targets==i)[0]
        plt.scatter(embeddings[inds,0], embeddings[inds,1], alpha=0.5, color=colors[i])
    if xlim:
        plt.xlim(xlim[0], xlim[1])
    if ylim:
        plt.ylim(ylim[0], ylim[1])
    plt.legend(object_classes)
    plt.show()

def extract_embeddings(dataloader, model):
    with torch.no_grad():
        model.eval()
        embeddings = np.zeros((len(dataloader.dataset), 2))
        labels = np.zeros(len(dataloader.dataset))
        k = 0
        for images, target in dataloader:
            if cuda:
                images = images.cuda()
            embeddings[k:k+len(images)] = model.get_embedding(images).data.cpu().numpy()
            labels[k:k+len(images)] = target.numpy()
            k += len(images)
    return embeddings, labels


def get_multivariate_gaussion_parameters(train_embeddings_tl, train_labels_tl):
    para = []
    labels_set = set(train_labels_tl)
    for label in labels_set:
        print("Label: {}".format(label))
        indies = train_labels_tl == label
        embeddings = train_embeddings_tl[indies]
        mean = np.mean(embeddings, axis=0)
        cov = np.matmul((embeddings - mean).transpose(), (embeddings - mean)) / len(embeddings)
        print("Mean: {}".format(mean))
        print("Cov: {}".format(cov))
        print("\n")
        para.append((mean, cov))
    return para

