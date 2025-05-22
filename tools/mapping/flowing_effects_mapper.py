import numpy as np
from tools.mapping import BaseMapper
from collections import deque

class FlowingEffectsMapper(BaseMapper):
    def __init__(self, width, height=1, history_length=10):
        super().__init__(width, height)
        self.history = deque(maxlen=history_length)
        self.phase = 0.0  # Controls movement

    def map(self, analysis_data):
        width = self.width
        output = np.zeros((1, width, 3), dtype=np.uint8)

        # === Audio Features ===
        bass = analysis_data["band_bass"]
        mid = analysis_data["band_mid"]
        high = analysis_data["band_high_mid"]
        loudness = np.clip(analysis_data["rms"], 0.0, 1.0)
        centroid = analysis_data["spectral_centroid"]
        flux = np.log1p(analysis_data["spectral_flux"])
        is_beat = analysis_data["is_beat"]

        # === Save history ===
        self.history.append({
            "bass": bass,
            "mid": mid,
            "high": high,
            "loudness": loudness,
            "centroid": centroid
        })

        avg = lambda key: np.mean([h[key] for h in self.history])

        # === Dynamic phase shift based on spectral centroid ===
        wave_speed = 0.2 + avg("centroid") / 5000.0
        self.phase += wave_speed

        for x in range(width):
            pos = x / width

            # === Sinus wave for movement across the strip ===
            wave = 0.5 + 0.5 * np.sin(2 * np.pi * pos + self.phase)

            # === Base color from feature blend (R=high, G=mid, B=bass) ===
            r = int(np.clip((avg("high") + wave) * 128, 0, 255))
            g = int(np.clip((avg("mid") + wave) * 128, 0, 255))
            b = int(np.clip((avg("bass") + wave) * 128, 0, 255))

            # === Brightness scaling from loudness ===
            brightness = avg("loudness")
            color = np.array([r, g, b]) * brightness

            # === Flux-driven jitter for more motion ===
            flux_jitter = int(min(flux * 10, 5))
            jitter = np.random.randint(-flux_jitter, flux_jitter + 1)
            j_x = np.clip(x + jitter, 0, width - 1)

            output[0, j_x] = np.clip(color, 0, 255)

        # === Beat flash (white pulse across the whole strip) ===
        if is_beat:
            strength = int(255 * avg("loudness"))
            output[0, :] = np.clip(output[0, :] + [strength] * 3, 0, 255)

        self.output = output
        return self.output.copy()
