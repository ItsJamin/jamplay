import numpy as np
from tools.mapping import BaseMapper

class EnergyFlowMapper(BaseMapper):
    def __init__(self, width, height, smoothing_factor=0.05):
        super().__init__(width, height)
        self.flow_state = np.random.rand(height, width, 3) * 0.2  # Initial low energy
        self.previous_color = np.zeros(3)  # Initialize previous color to black (no color)
        self.smoothing_factor = smoothing_factor  # Controls the smoothness of the color transition

    def map(self, analysis_data):
        # Extract spectral centroid from analysis data
        centroid = analysis_data.get("spectral_centroid", 0)

        # Normalize spectral centroid to range [0, 1]
        max_centroid = 22050  # Assuming the max frequency is Nyquist (half the sample rate for 44.1kHz)
        normalized_centroid = np.clip(centroid / max_centroid, 0, 1)

        # Map the normalized centroid to a color
        new_color = self.interpolate_color(normalized_centroid)

        # Smooth transition between the previous color and the new color
        smoothed_color = self.smooth_color(self.previous_color, new_color)

        # Create the layers for red, green, blue
        red_layer = np.zeros((self.height, self.width))
        green_layer = np.zeros((self.height, self.width))
        blue_layer = np.zeros((self.height, self.width))

        # Fill each layer with the smoothed color
        red_layer[:] = smoothed_color[0]
        green_layer[:] = smoothed_color[1]
        blue_layer[:] = smoothed_color[2]

        # Stack layers into RGB
        target = np.stack([red_layer, green_layer, blue_layer], axis=-1)

        # Smooth transition (decay + input)
        self.flow_state = 0.0 * self.flow_state + 1 * target

        # Update the previous color for the next iteration
        self.previous_color = smoothed_color

        # Return as uint8 RGB values (0-255)
        return (self.flow_state * 255).astype(np.uint8)

    def interpolate_color(self, normalized_centroid):
        """
        Interpolate color based on the spectral centroid.
        Low centroid (bass) -> Red, Mid -> Yellow/Green, High -> Blue
        """
        if normalized_centroid < 0.33:
            # Interpolate from Red to Yellow for low frequencies (bass)
            color = np.array([1, normalized_centroid * 3, 0])  # Red to Yellow
        elif normalized_centroid < 0.66:
            # Interpolate from Yellow to Green for mid frequencies
            color = np.array([1 - (normalized_centroid - 0.33) * 3, 1, 0])  # Yellow to Green
        else:
            # Interpolate from Green to Blue for high frequencies
            color = np.array([0, 1 - (normalized_centroid - 0.66) * 3, 1])  # Green to Blue

        return color

    def smooth_color(self, old_color, new_color):
        """
        Smooth the color transition by blending the old and new colors using exponential smoothing.
        """
        return (1 - self.smoothing_factor) * old_color + self.smoothing_factor * new_color
