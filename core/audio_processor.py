import numpy as np
import scipy.io.wavfile as wav

class AudioProcessor:
    """Handles FFT and waveform analysis."""

    def __init__(self, file):
        self.sr, data = wav.read(file)
        self.fft_length = 1024
        if len(data.shape) > 1:
            data = np.mean(data, axis=1)  # Convert to mono

        self.data = data.astype(np.float32) / np.max(np.abs(data))  # Normalize
        self.fft_data = np.fft.fft(self.data)  # Compute FFT for entire song
        self.magnitude = np.abs(self.fft_data) / np.max(np.abs(self.fft_data))  # Normalize FFT

    def get_fft_for_time(self, position):
        """Returns the FFT data for the given position."""
        i = int(position * self.sr)
        return self.magnitude[i:i + self.fft_length]  # Return a slice of FFT data
