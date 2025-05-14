import numpy as np
import colorsys
from tools.mapping import BaseMapper

class AdaptiveLineMapper(BaseMapper):
    def __init__(self, width, height, history_length=10):
        super().__init__(width, height)
        self.history_length = history_length
        self.history = [np.zeros((1, width, 3), dtype=np.float32) for _ in range(history_length)]
        self.current_mood = "cool"
        self.beat_phase = 0.0  # smooth beat modulation

    def map(self, analysis_data):
        # Robust extraction with fallback defaults
        bass = analysis_data.get("bass_level") or 0.0
        mid = analysis_data.get("mid_level") or 0.0
        melody = analysis_data.get("melody_energy") or 0.0
        loudness = analysis_data.get("loudness") or 0.0
        centroid = analysis_data.get("spectral_centroid") or 0.0
        flux = analysis_data.get("spectral_flux") or 0.0
        is_beat = analysis_data.get("is_beat") or False

        # Mood detection
        self.current_mood = self._detect_mood(melody, centroid, flux, mid)

        # Smooth beat handling
        if is_beat:
            self.beat_phase = 1.0
        else:
            self.beat_phase *= 0.9  # decay

        # Color generation
        base_line = self._generate_dynamic_color_line(
            mood=self.current_mood,
            loudness=loudness,
            centroid=centroid,
            melody=melody,
            beat_intensity=self.beat_phase
        )

        # Texture noise (subtle)
        base_line = self._add_texture_noise(base_line, flux)

        # Update history and apply smoothing
        self._update_history(base_line)
        smooth_line = self._get_smoothed_line(flux)

        # Final RGB output
        return np.clip(smooth_line, 0, 255).astype(np.uint8)

    def _detect_mood(self, melody, centroid, flux, mid):
        if flux > 6 and centroid > 5 and melody > 0.5:
            return "electronic"
        elif mid > 0.4 and melody < 0.3 and flux < 5:
            return "warm"
        else:
            return "cool"

    def _generate_dynamic_color_line(self, mood, loudness, centroid, melody, beat_intensity):
        # Normalize components
        hue_shift = np.clip(centroid / 10.0, 0.0, 1.0)
        saturation = np.clip(melody / 0.8, 0.3, 1.0)
        lightness = np.clip(loudness / 100.0, 0.2, 1.0)

        # Mood base hues
        mood_hues = {
            "cool": 0.55,        # cyan/blue
            "warm": 0.08,        # orange
            "electronic": 0.78,  # magenta/neon
        }
        base_hue = mood_hues.get(mood, 0.5)

        # Horizontal position (0–1 across width)
        x = np.linspace(0, 1, self.width).reshape(1, self.width, 1)

        # Beat wave pulse (subtle)
        beat_wave = np.sin(x * np.pi * 2 + self.beat_phase * np.pi) * beat_intensity * 0.1

        # Combine base hue with variation
        hues = (base_hue + (x - 0.5) * 0.2 + beat_wave) % 1.0

        # Convert HLS to RGB
        rgb = np.array([
            colorsys.hls_to_rgb(h, lightness, saturation)
            for h in hues.flatten()
        ]).reshape(1, self.width, 3)

        return (rgb * 255).astype(np.float32)

    def _add_texture_noise(self, line, flux):
        strength = np.clip(flux / 10.0, 0.0, 0.15)
        noise = (np.random.rand(1, self.width, 3) - 0.5) * 50 * strength
        return line + noise.astype(np.float32)

    def _update_history(self, line):
        self.history.pop(0)
        self.history.append(line)

    def _get_smoothed_line(self, flux):
        alpha = flux / 10.0
        alpha = np.clip(alpha, 0.1, 0.8)
        history_avg = np.mean(self.history, axis=0)
        latest = self.history[-1]
        return (1 - alpha) * history_avg + alpha * latest
