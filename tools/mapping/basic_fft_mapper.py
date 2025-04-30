import numpy as np
from tools.mapping import BaseMapper

class BasicFFTMapper(BaseMapper):
    def __init__(self, width, height):
        super().__init__(width, height)

    def map(self, analysis_data):
        fft = np.array(analysis_data["fft"])
        max_val = np.max(fft) if np.max(fft) > 0 else 1
        normalized = fft / max_val  # scale to [0, 1]

        num_bins = len(normalized)
        bar_width = self.width // num_bins

        output = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        for i, val in enumerate(normalized):
            height = int(val * self.height)
            for y in range(self.height - height, self.height):
                for x in range(i * bar_width, (i + 1) * bar_width):
                    if x < self.width:
                        output[y, x] = [0, 255, 0]  # green

        return output
