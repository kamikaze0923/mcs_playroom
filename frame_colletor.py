import numpy as np
from skimage import transform

class FrameCollector:
    def __init__(self):
        self.frames = []

    def add_frame(self, np_img):
        np_img /= 10000
        np_img *= 256
        np_img = transform.resize(np_img, (256, 256))
        np_img = np_img.astype('uint8')
        np_img = np.repeat(np_img[np.newaxis, :, :], 3, axis=0)
        self.frames.append(np_img)