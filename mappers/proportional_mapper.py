import numpy as np

class ProportionalMapper:
    """Maps a relative 2D visualization to a fixed pixel resolution."""

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def map(self, relative_image):
        """Scales the relative image to the desired resolution."""
        mapped_frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        scale_x = relative_image.shape[1] / self.width
        scale_y = relative_image.shape[0] / self.height

        for y in range(self.height):
            for x in range(self.width):
                mapped_frame[y, x] = relative_image[int(y * scale_y), int(x * scale_x)]

        return mapped_frame
