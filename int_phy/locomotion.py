
from locomotion.network import ObjectStatePrediction
from locomotion.train import MODEL_SAVE_DIR, HIDDEN_STATE_SIZE
import os
import torch



class LocomotionModel:
    def __init__(self):
        self.net = ObjectStatePrediction()
        self.net.eval()
        self.net.load_state_dict(
            torch.load(os.path.join(MODEL_SAVE_DIR, "model_{}_hidden_state.pth".format(HIDDEN_STATE_SIZE)),
                       map_location="cpu")
        )

    def predict(self, hidden_state, observation):
        pass


