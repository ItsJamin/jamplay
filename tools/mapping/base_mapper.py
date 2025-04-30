import numpy as np

class BaseMapper:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def map(self, analysis_data):
        """
        Returns an (H, W, 3) RGB array based on the analysis data.
        Should be overridden by subclasses.
        """
        return np.zeros((self.height, self.width, 3), dtype=np.uint8)