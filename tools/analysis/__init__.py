import numpy as np

# === Handle Audio File ===

audio_file = None
audio_length = 0   # in seconds
audio_props = { # calculated once for every songs 
    "beats": [],
    "bpm": None
}

def set_audio(data, sample_rate):
    global audio_file, audio_length
    if len(data.shape) == 2:
        data = data.mean(axis=1).astype(data.dtype)
    audio_file = normalize_audio(data)
    audio_length = len(data) / sample_rate

    analyze_full_audio(sample_rate=sample_rate)  


def normalize_audio(audio):
    if audio.dtype == np.int16:
        return audio.astype(np.float32) / 32768.0
    elif audio.dtype == np.int32:
        return audio.astype(np.float32) / 2147483648.0
    elif audio.dtype == np.uint8:
        return (audio.astype(np.float32) - 128) / 128.0
    else:
        return audio

def get_segment_at_time(timestamp, duration, sample_rate):
    global audio_file
    if audio_file is None:
        return np.zeros(int(duration * sample_rate))
    start = int(timestamp * sample_rate)
    end = start + int(duration * sample_rate)
    segment = np.zeros(int(duration * sample_rate))
    if 0 <= start < len(audio_file):
        available = audio_file[start:min(end, len(audio_file))]
        segment[:len(available)] = available
    return segment

# === Feature Calculations ===

# Frequency-Based Features

def compute_spectral_centroid(audio, sample_rate):
    N = len(audio)
    if N == 0:
        return 0.0
    windowed = audio * np.hanning(N)
    magnitude = np.abs(np.fft.fft(windowed))[:N//2]
    freqs = np.fft.fftfreq(N, d=1/sample_rate)[:N//2]
    if np.sum(magnitude) == 0:
        return 0.0
    return np.sum(freqs * magnitude) / np.sum(magnitude)

def compute_magnitude_spectrum(audio, sample_rate):
    """
    Computes the magnitude spectrum of an audio segment.
    Returns the frequency bins and the magnitudes.
    """
    N = len(audio)
    if N == 0:
        return np.array([]), np.array([])

    windowed = audio * np.hanning(N)  # Apply window function
    spectrum = np.fft.fft(windowed)  # FFT to get frequency content
    magnitude = np.abs(spectrum)[:N // 2]  # Magnitude spectrum
    freqs = np.fft.fftfreq(N, d=1/sample_rate)[:N // 2]  # Frequency bins

    return freqs, magnitude

# Time-relevant features

def compute_rms(audio):
    return np.sqrt(np.mean(audio**2))

def compute_energy(audio):
    return np.mean(audio**2)

def compute_spectral_flux(timestamp, sample_rate, frame_duration=0.1):
    """
    Computes the spectral flux between two consecutive frames (segments).
    """
    seg_prev = get_segment_at_time(timestamp - frame_duration, frame_duration, sample_rate)
    seg_curr = get_segment_at_time(timestamp, frame_duration, sample_rate)

    # Get magnitude spectra of both frames
    _, mag_prev = compute_magnitude_spectrum(seg_prev, sample_rate)
    _, mag_curr = compute_magnitude_spectrum(seg_curr, sample_rate)

    # Compute spectral flux (difference of magnitude spectra)
    diff = mag_curr - mag_prev
    diff[diff < 0] = 0  # Only positive changes contribute to flux
    flux = np.sum(diff ** 2)
    
    return flux

def compute_zero_crossing_rate(audio):
    """How often the signal passes the 0-line"""
    return np.sum(np.abs(np.diff(np.sign(audio)))) / len(audio)

def is_beat(timestamp, window_duration=0.1):
    """Checks precalculated beat array for beats in this time window"""
    for beat_time in audio_props["beats"]:
        if timestamp <= beat_time < timestamp + window_duration:
            return True
    return False

# === Main Analysis Entry Point ===

def analyze_segment(timestamp, sample_rate):
    segment_duration = 0.1  # seconds
    segment = get_segment_at_time(timestamp, segment_duration, sample_rate)

    freqs, magnitudes = compute_magnitude_spectrum(segment, sample_rate)
    normalized_magnitudes = magnitudes / max(magnitudes)

    analysis = {
        "rms": compute_rms(segment),
        "spectral_centroid": compute_spectral_centroid(segment, sample_rate),
        "spectral_flux": compute_spectral_flux(timestamp, sample_rate, segment_duration),
        "normalized_magnitudes": normalized_magnitudes,
        "zero_crossing_rate": compute_zero_crossing_rate(segment),
        "is_beat": is_beat(timestamp, segment_duration),
        "bpm": audio_props["bpm"]
    }

    return analysis

# === Full Audio Analysis at the Beginning ===

def detect_beats(sample_rate, frame_size=1024, hop_size=512):
    global audio_file, audio_props

    audio = audio_file
    if audio is None:
        return

    energies = []
    timestamps = []

    for i in range(0, len(audio) - frame_size, hop_size):
        frame = audio[i:i+frame_size]
        energy = compute_energy(frame)
        energies.append(energy)
        timestamps.append(i / sample_rate)

    energies = np.array(energies)
    mean_energy = np.mean(energies)
    std_energy = np.std(energies)

    audio_props["beats"] = [
        timestamps[i] for i in range(len(energies))
        if energies[i] > mean_energy + 1.5 * std_energy
    ]

    if len(audio_props["beats"]) > 1:
        min_dist = 0.3 # minimum distance between two beats else it would be over 200bpm, highly unlikely
        filtered_beats = [t for i, t in enumerate(audio_props["beats"]) if i == 0 or t - audio_props["beats"][i - 1] >= min_dist]
        intervals = np.diff(filtered_beats)
        avg_interval = np.median(intervals)
        audio_props["bpm"] = 60.0 / avg_interval
    else:
        audio_props["bpm"] = 0.0


# Here the function to compute it all

def analyze_full_audio(sample_rate):
    global audio_props
    # reset values
    audio_props["beats"] = []
    audio_props["bpm"] = None  

    detect_beats(sample_rate)
