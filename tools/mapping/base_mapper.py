import numpy as np

class BaseMapper:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.output = np.zeros((height, width, 3), dtype=np.uint8)

    def map(self, analysis_data):
        """
        Returns an (H, W, 3) RGB array based on the analysis data.
        Should be overridden by subclasses.
        """
        return self.output