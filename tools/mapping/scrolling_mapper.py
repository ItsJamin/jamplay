import numpy as np
from tools.mapping import BaseMapper


class ScrollingMapper(BaseMapper):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.scroll_x = 0

    def map(self, analysis_data):
        # Scroll canvas left by 1 pixel
        self.output[:, :-1] = self.output[:, 1:]
        self.output[:, -1] = 0  # Clear new rightmost column

        height = self.height
        x = self.width - 10  # Rightmost column

        # === Feature Extraction ===
        bass = analysis_data["band_bass"]
        mid = analysis_data["band_mid"]
        high = analysis_data["band_high_mid"]
        loudness = analysis_data["rms"]
        spectral_centroid = analysis_data["spectral_centroid"]
        spectral_flux = analysis_data["spectral_flux"]
        is_beat = analysis_data["is_beat"]

        # === Map frequency levels to Y positions ===

        # Scale for y-positioning
        bass_y = int((1+bass)/2 * height)
        mid_y = int((1+mid)/2 * height)
        high_y = int((1+high)/2 * height)

        self.output[bass_y, x] = [0, 0, 200]
        self.output[mid_y, x] = [0, 200, 0]
        self.output[high_y, x] = [200, 0, 0]

        # === Beat detection: white vertical line ===
        if is_beat:
            self.output[:int(height/4), x] = [255, 255, 255]

        # === Loudness: Color bar from bottom based on spectral centroid ===
        bar_height = int(loudness * height)  # max at half screen

        # Color based on spectral centroid: low -> blue, high -> red
        centroid_color = int(np.clip(spectral_centroid / (10 * 2), 0, 255))
        # Map spectral centroid to a gradient from blue to red
        color = [centroid_color, 0, 255 - centroid_color]  # RGB from Blue (low freq) to Red (high freq)

        # Fill the loudness bar with the calculated color
        if bar_height > 0:
            self.output[height - bar_height:height, x] = color  # Gradient color

        # === Spectral Flux: Blue bar from bottom with 1/4 max height ===
        normalized_flux = np.log1p(spectral_flux)
        flux_height = min(int(normalized_flux),(height // 4))  # 1/4 max height

        # Blue bar for spectral flux
        if flux_height > 0:
            self.output[height - flux_height: height, x] = [0, 255, 255]  # Blue

        vis_output = self.output.copy()

        # Add highlight to indicate current
        vis_output[:, x] = np.clip(vis_output[:, x] + 40, 0, 255)  # Brighten
        vis_output[0, x] = [255, 255, 0]  # Yellow top
        vis_output[-1, x] = [255, 255, 0]  # Yellow bottom

        return vis_output
