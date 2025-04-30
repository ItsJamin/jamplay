import numpy as np


def compute_fft(audio_segment, sample_rate, num_bins=50):
    fft_result = np.fft.rfft(audio_segment)
    magnitudes = np.abs(fft_result)
    freqs = np.fft.rfftfreq(len(audio_segment), d=1/sample_rate)

    bin_size = max(1, len(magnitudes) // num_bins)
    reduced_magnitudes = []
    reduced_freqs = []

    for i in range(0, len(magnitudes), bin_size):
        reduced_magnitudes.append(np.mean(magnitudes[i:i+bin_size]))
        reduced_freqs.append(np.mean(freqs[i:i+bin_size]))

    return np.array(reduced_magnitudes), np.array(reduced_freqs)


def get_audio_segment(audio_data, sample_rate, start_time, duration=0.1):
    start_sample = int(start_time * sample_rate)
    end_sample = start_sample + int(duration * sample_rate)
    return audio_data[start_sample:end_sample]


def normalize_amplitudes(magnitudes, max_height=200):
    max_value = np.max(magnitudes)
    if max_value > 0:
        normalized_magnitudes = (magnitudes / max_value) * max_height
    else:
        normalized_magnitudes = np.zeros_like(magnitudes)
    return normalized_magnitudes


def rms(audio_segment):
    return np.sqrt(np.mean(np.square(audio_segment)))


def zero_crossing_rate(audio_segment):
    return ((audio_segment[:-1] * audio_segment[1:]) < 0).sum() / len(audio_segment)


def spectral_centroid(magnitudes, sample_rate):
    freqs = np.fft.fftfreq(len(magnitudes), d=1/sample_rate)
    positive_freqs = freqs[:len(freqs) // 2]
    positive_magnitudes = magnitudes[:len(magnitudes) // 2]
    return np.sum(positive_freqs * positive_magnitudes) / (np.sum(positive_magnitudes) + 1e-10)


def spectral_bandwidth(audio_segment, sample_rate, centroid):
    magnitudes = np.abs(np.fft.rfft(audio_segment))
    freqs = np.fft.rfftfreq(len(audio_segment), d=1/sample_rate)
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

    if audio_segment.ndim > 1:
        audio_segment = np.mean(audio_segment, axis=1)

    fft, freqs = compute_fft(audio_segment, sample_rate)
    fft_normalized = normalize_amplitudes(np.array(fft), max_height=1.0)

    centroid = spectral_centroid(audio_segment, sample_rate)
    bandwidth = spectral_bandwidth(audio_segment, sample_rate, centroid)
    flux = spectral_flux(audio_segment, previous_segment_cache)
    zcr = zero_crossing_rate(audio_segment)
    rms_val = rms(audio_segment)

    is_silent = rms_val < 0.01

    # Bass: < 250 Hz
    bass_magnitudes = [mag for mag, freq in zip(fft_normalized, freqs) if freq < 250]
    bass_level = np.mean(bass_magnitudes) if bass_magnitudes else 0.0
    
    # Mid: 250 Hz to 2 kHz
    mid_magnitudes = [mag for mag, freq in zip(fft_normalized, freqs) if 250 <= freq < 1000]
    mid_level = np.mean(mid_magnitudes) if mid_magnitudes else 0.0
    
    # Treble: > 2 kHz
    treble_magnitudes = [mag for mag, freq in zip(fft_normalized, freqs) if freq >= 1000]
    treble_level = np.mean(treble_magnitudes) if treble_magnitudes else 0.0

    # Overall energy: consider all frequency ranges
    overall_energy = np.mean(fft_normalized)

    # Melody energy: this range can vary based on your preference, but let's take 10 Hz to 2000 Hz
    melody_magnitudes = [mag for mag, freq in zip(fft_normalized, freqs) if 10 <= freq < 2000]
    melody_energy = np.mean(melody_magnitudes) if melody_magnitudes else 0.0

    # High frequency energy: this could be anything above 2000 Hz
    high_freq_magnitudes = [mag for mag, freq in zip(fft_normalized, freqs) if freq >= 2000]
    high_freq_energy = np.mean(high_freq_magnitudes) if high_freq_magnitudes else 0.0

    analysis = {
        "fft": fft_normalized,
        "bass_level": bass_level,
        "mid_level": mid_level,
        "treble_level": treble_level,
        "overall_energy": overall_energy,
        "melody_energy": melody_energy,
        "high_freq_energy": high_freq_energy,
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
