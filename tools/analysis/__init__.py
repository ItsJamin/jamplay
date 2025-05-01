import numpy as np


# === Core Audio Analysis Functions ===
def compute_fft(audio_segment, sample_rate, num_bins=50):
    fft_result = np.fft.rfft(audio_segment)
    magnitudes = np.abs(fft_result)
    freqs = np.fft.rfftfreq(len(audio_segment), d=1/sample_rate)

    bin_size = max(1, len(magnitudes) // num_bins)
    reduced_magnitudes = [np.mean(magnitudes[i:i+bin_size]) for i in range(0, len(magnitudes), bin_size)]
    reduced_freqs = [np.mean(freqs[i:i+bin_size]) for i in range(0, len(freqs), bin_size)]

    return np.array(reduced_magnitudes), np.array(reduced_freqs)


def get_audio_segment(audio_data, sample_rate, start_time, duration=0.1):
    start_sample = int(start_time * sample_rate)
    end_sample = start_sample + int(duration * sample_rate)
    return audio_data[start_sample:end_sample]


def normalize_amplitudes(magnitudes, max_height=200):
    magnitudes = np.log1p(magnitudes)
    max_value = np.max(magnitudes)
    return (magnitudes / max_value) * max_height if max_value > 0 else np.zeros_like(magnitudes)


def compute_basic_metrics(audio_segment):
    rms_val = np.sqrt(np.mean(np.square(audio_segment)))
    zcr = ((audio_segment[:-1] * audio_segment[1:]) < 0).sum() / len(audio_segment)
    loudness = 20 * np.log10(rms_val + 1e-10)
    dynamic_range = np.max(audio_segment) - np.min(audio_segment)
    return rms_val, zcr, loudness, dynamic_range


def compute_spectral_features(audio_segment, sample_rate):
    magnitudes = np.abs(np.fft.rfft(audio_segment))
    freqs = np.fft.rfftfreq(len(audio_segment), d=1/sample_rate)
    centroid = np.sum(freqs * magnitudes) / (np.sum(magnitudes) + 1e-10)
    bandwidth = np.sqrt(np.sum(((freqs - centroid) ** 2) * magnitudes) / (np.sum(magnitudes) + 1e-10))
    return centroid, bandwidth


def spectral_flux(current_segment, previous_segment):
    if previous_segment is None or len(previous_segment) != len(current_segment):
        return 0.0
    curr_mag = np.abs(np.fft.rfft(current_segment))
    prev_mag = np.abs(np.fft.rfft(previous_segment))
    return np.sum((curr_mag - prev_mag) ** 2)


def compute_frequency_bands(fft_normalized, freqs):
    bass = [mag for mag, freq in zip(fft_normalized, freqs) if freq < 250]
    mid = [mag for mag, freq in zip(fft_normalized, freqs) if 250 <= freq < 1000]
    treble = [mag for mag, freq in zip(fft_normalized, freqs) if freq >= 1000]
    melody = [mag for mag, freq in zip(fft_normalized, freqs) if 100 <= freq < 2000]
    high = [mag for mag, freq in zip(fft_normalized, freqs) if freq >= 2000]
    return bass, mid, treble, melody, high


# === Persistent Cache ===
previous_segment_cache = None
previous_energy_value = 0.0
previous_flux_values = []

def new_music():
    global previous_segment_cache, previous_energy_value, previous_flux_values
    previous_segment_cache = None
    previous_energy_value = 0.0
    previous_flux_values = []


# === Main Analysis Entry Point ===
def analyze_segment(audio_segment, sample_rate):
    global previous_segment_cache, previous_energy_value, previous_flux_values

    if audio_segment.ndim > 1:
        audio_segment = np.mean(audio_segment, axis=1)

    fft, freqs = compute_fft(audio_segment, sample_rate)
    fft_normalized = normalize_amplitudes(np.array(fft), max_height=1.0)

    centroid, bandwidth = compute_spectral_features(audio_segment, sample_rate)
    flux = spectral_flux(audio_segment, previous_segment_cache)
    rms_val, zcr, loudness, dynamic_range = compute_basic_metrics(audio_segment)

    is_silent = rms_val < 0.01
    overall_energy = np.mean(fft_normalized)
    energy_change = overall_energy - previous_energy_value
    previous_energy_value = overall_energy

    bass, mid, treble, melody, high = compute_frequency_bands(fft_normalized, freqs)
    bass_level = np.mean(bass) if bass else 0.0
    mid_level = np.mean(mid) if mid else 0.0
    treble_level = np.mean(treble) if treble else 0.0
    melody_energy = np.mean(melody) if melody else 0.0
    high_freq_energy = np.mean(high) if high else 0.0

    total_energy = overall_energy + 1e-6
    bass_ratio = bass_level / total_energy
    mid_ratio = mid_level / total_energy
    treble_ratio = treble_level / total_energy

    spectral_contrast = np.std(fft_normalized)

    previous_flux_values.append(flux)
    if len(previous_flux_values) > 5:
        previous_flux_values.pop(0)
    is_beat = flux > 2.0 * np.mean(previous_flux_values)
    attack = max(0.0, flux - zcr)

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
        "loudness": loudness,
        "dynamic_range": dynamic_range,
        "energy_change": energy_change,
        "bass_ratio": bass_ratio,
        "mid_ratio": mid_ratio,
        "treble_ratio": treble_ratio,
        "spectral_contrast": spectral_contrast,
        "is_beat": is_beat,
        "attack": attack,
        "tempo_estimate": 0.0,
        "is_silent": is_silent,
    }

    previous_segment_cache = audio_segment.copy()

    return analysis
