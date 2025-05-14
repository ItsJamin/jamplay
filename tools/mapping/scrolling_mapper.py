import numpy as np
from tools.mapping import BaseMapper


class ScrollingMapper(BaseMapper):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.output = np.zeros((height, width, 3), dtype=np.uint8)
        self.scroll_x = 0

    def map(self, analysis_data):
        # Scroll canvas left by 1 pixel
        self.output[:, :-1] = self.output[:, 1:]
        self.output[:, -1] = 0  # Clear new rightmost column

        height = self.height
        x = self.width - 1  # Rightmost column

        # === Feature Extraction ===
        bass = analysis_data["bass_ratio"]
        mid = analysis_data["mid_ratio"]
        treble = analysis_data["treble_ratio"]
        melody = analysis_data["melody_ratio"]
        high = analysis_data["high_ratio"]
        loudness = analysis_data["loudness"]
        spectral_centroid = analysis_data["spectral_centroid"]
        spectral_flux = analysis_data["spectral_flux"]
        is_beat = analysis_data["is_beat"]

        # === Map frequency levels to Y positions ===

        # Scale for y-positioning
        bass_y = int((height-1) * (1.0 - bass))
        mid_y = int((height-1) * (1.0 - mid))
        melody_y = int((height-1) * (1.0 - melody))
        treble_y = int((height-1) * (1.0 - treble))
        high_y = int((height - 1) * (1.0 - high))

        self.output[bass_y, x] = [0, 0, 200]
        self.output[melody_y, x] = [000, 100, 200]
        self.output[mid_y, x] = [0, 200, 0]
        self.output[treble_y, x] = [200, 100, 0]
        self.output[high_y, x] = [200, 0, 0]

        # === Beat detection: white vertical line ===
        if is_beat:
            self.output[:, x] = [255, 255, 255]

        # === Loudness: Color bar from bottom based on spectral centroid ===
        normalized_loudness = np.clip((loudness) / 100, 0, 1)
        bar_height = int(normalized_loudness * (height // 2))  # max at half screen

        # Color based on spectral centroid: low -> blue, high -> red
        centroid_color = int(np.clip(spectral_centroid / (10 * 2), 0, 255))
        # Map spectral centroid to a gradient from blue to red
        color = [centroid_color, 0, 255 - centroid_color]  # RGB from Blue (low freq) to Red (high freq)

        # Fill the loudness bar with the calculated color
        if bar_height > 0:
            self.output[height - bar_height:height, x] = color  # Gradient color

        # === Spectral Flux: Blue bar from bottom with 1/4 max height ===
        normalized_flux = np.clip(spectral_flux / 10, 0, 1)  # Scale flux to fit the range
        flux_height = int(normalized_flux * (height // 4))  # 1/4 max height

        # Blue bar for spectral flux
        if flux_height > 0:
            self.output[height - flux_height: height, x] = [0, 255, 255]  # Blue

        return self.output
