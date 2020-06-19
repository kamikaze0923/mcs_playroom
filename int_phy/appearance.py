import torch
from appearance.networks import EmbeddingNet
from appearance.train import MODEL_SAVE_DIR
from int_phy_recollect_appearance import SHAPE_TYPES
import os



class ApearanceTracker:
    def __init__(self):
        self.appearance_model = EmbeddingNet()
        self.appearance_model.load_state_dict(torch.load(os.path.join(MODEL_SAVE_DIR, "model.pth"), map_location="cpu"))
        self.appearance_distributions = []
        distribution_parameters = torch.load(os.path.join(MODEL_SAVE_DIR, "embedding_distribution.pth"), map_location="cpu")
        for _, x in enumerate(SHAPE_TYPES):
            mean = distribution_parameters["{}_mean".format(x)]
            cov = distribution_parameters["{}_cov".format(x)]
            distribution = torch.distributions.MultivariateNormal(loc=mean, covariance_matrix=cov)
            self.appearance_distributions.append(distribution)

    def get_appearance(self, object_frame):
        embedding = self.appearance_model(object_frame)
        return embedding[0].detach()