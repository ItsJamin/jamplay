import numpy as np

def compute_fft(audio_segment, sample_rate, num_bins=50):
    """
    Computes the FFT of a given audio segment and returns frequency magnitudes.

    :param audio_segment: The audio samples of the current time window.
    :param sample_rate: The sample rate of the audio.
    :param num_bins: The number of frequency bins to reduce the FFT output.
    :return: Frequency bins and their magnitudes.
    """
    fft_result = np.fft.rfft(audio_segment)
    magnitudes = np.abs(fft_result)
    freqs = np.fft.rfftfreq(len(audio_segment), d=1/sample_rate)

    # Reduce the number of frequency bins for visualization
    bin_size = len(freqs) // num_bins
    reduced_magnitudes = [np.mean(magnitudes[i:i+bin_size]) for i in range(0, len(magnitudes), bin_size)]
    return reduced_magnitudes

def get_audio_segment(audio_data, sample_rate, start_time, duration=0.1):
    """
    Extracts a short segment of audio data based on the current song position.

    :param audio_data: Full audio file data as a NumPy array.
    :param sample_rate: Sample rate of the audio.
    :param start_time: The starting time (in seconds) of the segment.
    :param duration: The duration (in seconds) of the segment.
    :return: Extracted segment of audio data.
    """
    start_sample = int(start_time * sample_rate)
    end_sample = start_sample + int(duration * sample_rate)
    return audio_data[start_sample:end_sample]

def normalize_amplitudes(magnitudes, max_height):
    """
    Normalizes the amplitude values to fit within a specified max height.

    :param magnitudes: The raw frequency magnitudes.
    :param max_height: The max height of the visualization bars.
    :return: Normalized amplitude values.
    """
    max_value = max(magnitudes) if max(magnitudes) > 0 else 1
    return [int((m / max_value) * max_height) for m in magnitudes]
