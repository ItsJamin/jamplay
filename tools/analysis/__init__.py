import numpy as np

# === Handle Audio File ===
audio_file = None
audio_length = 0   # in seconds

def set_audio(data, sample_rate):
    """
    Sets the global audio buffer.
    data: 1D numpy array, mono
    sample_rate: in Hz
    """
    global audio_file, audio_length
    # always mono
    if len(data.shape) == 2:
        data = data.mean(axis=1).astype(data.dtype)
    audio_file = normalize_audio(data)
    audio_length = len(data) / sample_rate


def normalize_audio(audio):
    if audio.dtype == np.int16:
        return audio.astype(np.float32) / 32768.0
    elif audio.dtype == np.int32:
        return audio.astype(np.float32) / 2147483648.0
    elif audio.dtype == np.uint8:
        return (audio.astype(np.float32) - 128) / 128.0
    else:
        return audio  # already float

def get_segment_at_time(timestamp, duration, sample_rate):
    """
    Returns a slice of the audio_file at a given timestamp and duration.
    This allows different features to have different sized timeframes.
    If out-of-bounds, returns zeros.
    """
    global audio_file
    if audio_file is None:
        return np.zeros(int(duration * sample_rate))

    start = int(timestamp * sample_rate)
    end = start + int(duration * sample_rate)

    if start < 0 or end > len(audio_file):
        segment = np.zeros(int(duration * sample_rate))
        if 0 <= start < len(audio_file):
            available = audio_file[start:min(end, len(audio_file))]
            segment[:len(available)] = available
        return segment
    return audio_file[start:end]


# === Calculating Functions ===
def compute_rms(audio):
    return np.sqrt(np.mean(audio**2))

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

# === Main Analysis Entry Point ===
def analyze_segment(timestamp, sample_rate):
    """
    timestamp: float, seconds
    sample_rate: int
    returns a dictionary of feature values
    """
    segment_duration = 0.1  # seconds
    segment = get_segment_at_time(timestamp, segment_duration, sample_rate)

    analysis = {
        "rms": compute_rms(segment),
        "spectral_centroid": compute_spectral_centroid(segment, sample_rate),
        # LATER TODO: add more features here
    }

    return analysis