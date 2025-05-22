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

        # === History
        self.history.append({
            "bass": bass,
            "mid": mid,
            "high": high,
            "loudness": loudness,
            "centroid": centroid
        })

        avg = lambda key: np.mean([h[key] for h in self.history])

        # === Main wave phase (based on spectral centroid)
        wave_speed = 0.2 + avg("centroid") / 5000.0
        self.phase += wave_speed

        # === Beat phase (moves backwards on each beat)
        if not hasattr(self, "beat_phase"):
            self.beat_phase = 0.0
        if not hasattr(self, "beat_decay"):
            self.beat_decay = 0.0

        # Trigger counter-wave on beat
        if is_beat:
            self.beat_decay = 1.0  # full strength
        else:
            self.beat_decay *= 0.9  # decay over time

        self.beat_phase -= 0.6 * self.beat_decay  # backward movement

        for x in range(width):
            pos = x / width

            # === Main wave (rightward)
            main_wave = 0.5 + 0.5 * np.sin(2 * np.pi * pos + self.phase)

            # === Beat wave (leftward)
            beat_wave = 0.5 + 0.5 * np.sin(2 * np.pi * pos + self.beat_phase)

            # === Blend both waves
            wave = main_wave * (1.0 - self.beat_decay) + beat_wave * self.beat_decay

            # === Audio-based RGB
            r = int(np.clip((avg("high") + wave) * 128, 0, 255))
            g = int(np.clip((avg("mid") + wave) * 128, 0, 255))
            b = int(np.clip((avg("bass") + wave) * 128, 0, 255))

            # === Brightness
            brightness = np.clip((avg("loudness") * 3) ** 0.7, 0.05, 1.0)
            color = np.array([r, g, b]) * brightness

            # === Flux jitter
            flux_jitter = int(min(flux * 10, 5))
            jitter = np.random.randint(-flux_jitter, flux_jitter + 1)
            j_x = np.clip(x + jitter, 0, width - 1)

            output[0, j_x] = np.clip(color, 0, 255)

        self.output = output
        return self.output.copy()
