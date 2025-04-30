import numpy as np


def compute_fft(audio_segment, sample_rate, num_bins=50):
    fft_result = np.fft.rfft(audio_segment)
    magnitudes = np.abs(fft_result)
    freqs = np.fft.rfftfreq(len(audio_segment), d=1/sample_rate)

    bin_size = max(1, len(magnitudes) // num_bins)
    reduced_magnitudes = [np.mean(magnitudes[i:i+bin_size]) for i in range(0, len(magnitudes), bin_size)]
    return reduced_magnitudes


def get_audio_segment(audio_data, sample_rate, start_time, duration=0.1):
    start_sample = int(start_time * sample_rate)
    end_sample = start_sample + int(duration * sample_rate)
    return audio_data[start_sample:end_sample]


def normalize_amplitudes(magnitudes, max_height):
    max_value = max(magnitudes) if max(magnitudes) > 0 else 1
    return [int((m / max_value) * max_height) for m in magnitudes]


def rms(audio_segment):
    return np.sqrt(np.mean(np.square(audio_segment)))


def zero_crossing_rate(audio_segment):
    return ((audio_segment[:-1] * audio_segment[1:]) < 0).sum() / len(audio_segment)

def spectral_centroid(magnitudes, sample_rate):
    """
    Computes the spectral centroid, which is the weighted mean of the frequency spectrum,
    and provides an indication of the brightness of the sound.
    
    :param magnitudes: The magnitude of the frequencies (1D or 2D array).
    :param sample_rate: The sample rate of the audio.
    """
    
    # Compute the frequency bins
    freqs = np.fft.fftfreq(len(magnitudes), d=1/sample_rate)
    
    # Ensure that we are only using positive frequencies (half of the FFT spectrum)
    positive_freqs = freqs[:len(freqs) // 2]
    positive_magnitudes = magnitudes[:len(magnitudes) // 2]
    
    # Calculate the spectral centroid
    return np.sum(positive_freqs * positive_magnitudes) / (np.sum(positive_magnitudes) + 1e-10)

def spectral_bandwidth(audio_segment, sample_rate, centroid):

    magnitudes = np.abs(np.fft.rfft(audio_segment))
    freqs = np.fft.rfftfreq(len(audio_segment), d=1/sample_rate)
    print(magnitudes)
    print(freqs)
    return np.sqrt(np.sum(((freqs - centroid) ** 2) * magnitudes) / (np.sum(magnitudes) + 1e-10))


def spectral_flux(current_segment, previous_segment):
    if previous_segment is None or len(previous_segment) != len(current_segment):
        return 0.0
    curr_mag = np.abs(np.fft.rfft(current_segment))
    prev_mag = np.abs(np.fft.rfft(previous_segment))
    return np.sum((curr_mag - prev_mag) ** 2)


previous_segment_cache = None

def analyze_segment(audio_segment, sample_rate):
    global previous_segment_cache

    # Convert to mono once for all downstream functions
    if audio_segment.ndim > 1:
        audio_segment = np.mean(audio_segment, axis=1)

    fft = compute_fft(audio_segment, sample_rate)
    centroid = spectral_centroid(audio_segment, sample_rate)
    bandwidth = spectral_bandwidth(audio_segment, sample_rate, centroid)
    flux = spectral_flux(audio_segment, previous_segment_cache)
    zcr = zero_crossing_rate(audio_segment)
    rms_val = rms(audio_segment)

    is_silent = rms_val < 0.01

    analysis = {
        "fft": fft,
        "bass_level": np.mean(fft[:5]),
        "mid_level": np.mean(fft[5:15]),
        "treble_level": np.mean(fft[30:]),
        "overall_energy": np.mean(fft),
        "melody_energy": np.mean(fft[10:20]),
        "high_freq_energy": np.mean(fft[30:]),
        "energy_delta": 0.0,
        "spectral_centroid": centroid,
        "spectral_bandwidth": bandwidth,
        "spectral_flux": flux,
        "zero_crossing_rate": zcr,
        "rms": rms_val,
        "tempo_estimate": 0.0,
        "is_silent": is_silent,
    }

    previous_segment_cache = audio_segment.copy()

    return analysis
