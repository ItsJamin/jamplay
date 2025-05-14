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


# === Main Analysis Entry Point ===
def analyze_segment(timestamp, sample_rate):
    """
    timestamp: float, seconds
    sample_rate: int
    returns a dictionary of feature values
    """

    analysis = {
    }

    return analysis