import torch
from int_phy.appearance.networks import EmbeddingNet
from int_phy.appearance.train import MODEL_SAVE_DIR as APPEARANCE_MODEL_SAVE_DIR
from int_phy.locomotion.network import ObjectStatePrediction, HIDDEN_STATE_SIZE
from int_phy.locomotion.train import MODEL_SAVE_DIR as LOCOMOTION_MODEL_SAVE_DIR
from int_phy_recollect_appearance import SHAPE_TYPES
import os



class ApearanceModel:
    def __init__(self):
        self.appearance_model = EmbeddingNet()
        self.appearance_model.load_state_dict(
            torch.load(os.path.join(APPEARANCE_MODEL_SAVE_DIR, "model.pth"), map_location="cpu")
        )
        self.appearance_distributions = []
        distribution_parameters = torch.load(
            os.path.join(APPEARANCE_MODEL_SAVE_DIR, "embedding_distribution.pth"), map_location="cpu"
        )
        for _, x in enumerate(SHAPE_TYPES):
            mean = distribution_parameters["{}_mean".format(x)]
            cov = distribution_parameters["{}_cov".format(x)]
            distribution = torch.distributions.MultivariateNormal(loc=mean, covariance_matrix=cov)
            self.appearance_distributions.append(distribution)

    def get_appearance(self, object_frame):
        embedding = self.appearance_model(object_frame)
        return embedding[0].detach()

    def check_appearance(self, cropped_image, object_classes):
        appearance = self.get_appearance(cropped_image)
        max_likelihood_class = None
        max_likelihood = 0
        for distribution, class_name in zip(self.appearance_distributions, object_classes):
            log_prob = distribution.log_prob(appearance)
            prob = torch.exp(log_prob)
            if prob > max_likelihood:
                max_likelihood = prob
                max_likelihood_class = class_name
        return max_likelihood_class, max_likelihood

class LocomotionModel:

    LOCOMOTION_MSE_ERROR_THRESHOLD = 0.8
    LOCOMOTION_MSE_ERROR_THRESHOLD_UNSEEN = 1
    LEAVE_SCENE_PROB_TRESHOLD = 0.01

    def __init__(self):
        self.net = ObjectStatePrediction()
        self.net.eval()
        self.net.load_state_dict(
            torch.load(
                os.path.join(
                    LOCOMOTION_MODEL_SAVE_DIR, "model_{}_hidden_state.pth".format(HIDDEN_STATE_SIZE)
                ), map_location="cpu"
            )
        )

    def predict(self, observation, h_t, c_t):
        return self.net((observation, h_t, c_t))