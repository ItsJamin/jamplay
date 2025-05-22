"""
Feelgood Mapper
---

Goals: 
- Make good visualizations fitting the spirit of the song. 
    - More than just a one-trick-pony: Many Visualizations have just one type of visualization which leads to music being defined by the visualizer and not the other way around.
    - A little bit of randomness: The visualization should be to some degree predictable to give a good picture of the music. But if it is 100% predictable, it can quickly become boring.
- Optimized for an LED-Strip (1-dimensional, additive color(?))
    - Makes 1-dimensional output and stretches it into 2-dimension when needed


Ideas:
- Phases: Can we divide the song globally in parts? Do we need to?

- While Beat-Phase, beats do steps through a color scheme, in other phases the spectrum should have more influence on color
"""

from tools.mapping import BaseMapper
import numpy as np

# === MAPPER ===================================================================

class FeelGoodMapper(BaseMapper):

    def __init__(self, width, height):
        super().__init__(width, height)
        self.output = np.zeros((1, width, 3), dtype=np.uint8)

        self.ALPHA = 0.1
    
    def map(self, analysis_data):
        print(analysis_data)
        self.last_output = self.output.copy()
        # --- Available Features ------
        spectral_centroid = analysis_data["spectral_centroid"]
        loudness = analysis_data["rms"]
        freq_range = analysis_data["sample_rate"] // 2
        is_beat = analysis_data["is_beat"]
        flux = analysis_data["spectral_flux"]

        # --- Artists Part ------------
        centroid_color = int(np.clip(spectral_centroid / freq_range, 0, 255))
        color = [spectral_centroid, loudness * 20 * 255, 255 - centroid_color]

        if is_beat:
            color = [200, 200, 200]
        
        self.output[:] = color
        self.output = (self.output / 20).astype(np.uint8)

        # --- Final Filter ------------
        #self.output = lerp_frames(self.last_output, self.output, alpha=np.clip(0.5 + flux/10000, 0.1, 0.9))
        return np.tile(self.output, (self.height, 1)) # return as 2d-array


# === HELP FUNCTIONS ============================================================

def lerp_frames(last_frame, new_frame, alpha):
    """
    Linearly interpolate between last_frame and new_frame using alpha.
    Both frames must be of shape (1, width, 3).
    """
    return ((1 - alpha) * last_frame + alpha * new_frame).astype(np.uint8)
