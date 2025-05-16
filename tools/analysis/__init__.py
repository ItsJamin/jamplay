import numpy as np
from typing import Dict, Tuple, Optional

# === CONSTANTS =================================================================
SUBBAND_RANGES = {
    "band_sub_bass": (20, 60),
    "band_bass": (60, 250),
    "band_low_mid": (250, 500),
    "band_mid": (500, 2000),
    "band_high_mid": (2000, 4000),
    "band_presence": (4000, 6000),
    "band_brilliance": (6000, 20000)
}

DEFAULT_FEATURES = {
    "rms": 0.0,
    "zero_crossing_rate": 0.0,
    "is_silent": True,
    "is_beat": False,
    "bpm": 0.0,
    "spectral_centroid": 0.0,
    "normalized_magnitudes": np.array([]),
    "spectral_flux": 0.0,
    **{band: 0.0 for band in SUBBAND_RANGES}
}

ANALYSIS_WINDOW = 0.1  # Seconds for analysis frames
BEAT_MIN_INTERVAL = 0.3  # Minimum time between beats (200 BPM max)
SILENCE_THRESHOLD = 0.005  # RMS threshold for silence detection
EPSILON = 1e-9  # Small value to prevent division by zero

# === GLOBAL STATE =============================================================
_audio_buffer: Optional[np.ndarray] = None
_sample_rate: int = 44100
_audio_length: float = 0.0
_audio_props: Dict = {
    "beats": [],
    "bpm": None,
    "subband_stats": {"means": {}, "stds": {}},
}
_global_calculated = False

# === CORE AUDIO HANDLING ======================================================
def set_audio(data: np.ndarray, sample_rate: int) -> None:
    """Initialize audio analysis system with normalized audio data"""
    global _audio_buffer, _sample_rate, _audio_length, _global_calculated
    
    # Convert stereo to mono if needed
    if len(data.shape) == 2:
        data = data.mean(axis=1).astype(data.dtype)
    
    _audio_buffer = _normalize_audio(data)
    _sample_rate = sample_rate
    _audio_length = len(data) / sample_rate
    _global_calculated = False
    
    _analyze_full_audio()

def get_segment_at_time(timestamp: float, duration: float) -> np.ndarray:
    """Extract audio segment with zero-padding if out of bounds"""
    if _audio_buffer is None:
        return np.zeros(int(duration * _sample_rate))
    
    start = int(timestamp * _sample_rate)
    end = start + int(duration * _sample_rate)
    segment = np.zeros(int(duration * _sample_rate))
    
    if 0 <= start < len(_audio_buffer):
        available = _audio_buffer[start:min(end, len(_audio_buffer))]
        segment[:len(available)] = available
    
    return segment

def _normalize_audio(audio: np.ndarray) -> np.ndarray:
    """Normalize different integer formats to [-1.0, 1.0] floats"""
    if audio.dtype == np.int16:
        return audio.astype(np.float32) / 32768.0
    elif audio.dtype == np.int32:
        return audio.astype(np.float32) / 2147483648.0
    elif audio.dtype == np.uint8:
        return (audio.astype(np.float32) - 128) / 128.0
    return audio.astype(np.float32)

# === SPECTRAL ANALYSIS ========================================================
def _a_weighting(frequencies: np.ndarray) -> np.ndarray:
    """
    Calculate A-weighting coefficients for frequency array.
    Based on IEC 61672:2003 standard.
    """
    f_sq = np.square(frequencies)
    numerator = (12200**2 * f_sq**2)
    denominator = (f_sq + 20.6**2) * np.sqrt((f_sq + 107.7**2) * (f_sq + 737.9**2)) * (f_sq + 12200**2)
    return numerator / (denominator + EPSILON)

def _compute_subband_energies(freqs: np.ndarray, magnitudes: np.ndarray) -> Dict[str, float]:
    """Calculate energy in each frequency band with A-weighting applied"""
    weights = _a_weighting(freqs)
    weighted = magnitudes * weights
    
    energies = {}
    for band, (low, high) in SUBBAND_RANGES.items():
        mask = (freqs >= low) & (freqs < high)
        energies[band] = np.sum(weighted[mask]**2)
    
    return energies

def _calculate_global_subband_stats() -> None:
    """Pre-calculate subband statistics for the entire track"""
    frame_size = int(ANALYSIS_WINDOW * _sample_rate)
    energies = {band: [] for band in SUBBAND_RANGES}
    
    for i in range(0, len(_audio_buffer) - frame_size, frame_size):
        frame = _audio_buffer[i:i+frame_size]
        freqs, mag = compute_magnitude_spectrum(frame)
        band_energy = _compute_subband_energies(freqs, mag)
        
        for band, energy in band_energy.items():
            energies[band].append(energy)
    
    for band in SUBBAND_RANGES:
        arr = np.array(energies[band])
        _audio_props["subband_stats"]["means"][band] = np.mean(arr)
        _audio_props["subband_stats"]["stds"][band] = np.std(arr) + EPSILON

# === FEATURE CALCULATIONS =====================================================
def compute_magnitude_spectrum(audio: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Compute frequency bins and magnitude spectrum for audio segment"""
    N = len(audio)
    if N == 0:
        return np.array([]), np.array([])
    
    windowed = audio * np.hanning(N)
    spectrum = np.fft.fft(windowed)
    magnitude = np.abs(spectrum[:N//2])
    freqs = np.fft.fftfreq(N, d=1/_sample_rate)[:N//2]
    
    return freqs, magnitude

def compute_spectral_centroid(freqs: np.ndarray, magnitudes: np.ndarray) -> float:
    """Calculate spectral centroid from frequency spectrum"""
    if np.sum(magnitudes) == 0:
        return 0.0
    return np.sum(freqs * magnitudes) / np.sum(magnitudes)

def compute_spectral_flux(current_mag: np.ndarray, previous_mag: np.ndarray) -> float:
    """Calculate spectral flux between consecutive frames"""
    diff = current_mag - previous_mag
    diff[diff < 0] = 0  # Only consider increases
    return np.sum(diff**2)

# === TEMPO ANALYSIS ===========================================================
def _detect_beats() -> None:
    """Simple beat detection using energy thresholding"""
    frame_size = 1024
    hop_size = 512
    energies = []
    timestamps = []
    
    for i in range(0, len(_audio_buffer) - frame_size, hop_size):
        frame = _audio_buffer[i:i+frame_size]
        energies.append(compute_energy(frame))
        timestamps.append(i / _sample_rate)
    
    energies = np.array(energies)
    threshold = np.mean(energies) + 1.5 * np.std(energies)
    
    _audio_props["beats"] = [t for t, e in zip(timestamps, energies) if e > threshold]
    
    # Filter beats with minimum interval
    filtered = []
    for beat in _audio_props["beats"]:
        if not filtered or (beat - filtered[-1]) >= BEAT_MIN_INTERVAL:
            filtered.append(beat)
    
    # Calculate BPM from median interval
    if len(filtered) > 1:
        intervals = np.diff(filtered)
        _audio_props["bpm"] = 60 / np.median(intervals)
    else:
        _audio_props["bpm"] = 0.0

# === MAIN ANALYSIS ENTRY POINTS ===============================================
def _analyze_full_audio() -> None:
    global _global_calculated
    """Full audio preprocessing pipeline"""
    _audio_props.update({"beats": [], "bpm": None, "subband_stats": {"means": {}, "stds": {}},})
    _detect_beats()
    _calculate_global_subband_stats()
    _global_calculated = True

def analyze_segment(timestamp: float) -> Dict:
    """Get audio features with progressive enhancement of global features"""

    result = DEFAULT_FEATURES.copy()
    segment = get_segment_at_time(timestamp, ANALYSIS_WINDOW)

    # Time-domain features
    result.update({
        "rms": compute_rms(segment),
        "zero_crossing_rate": compute_zero_crossing_rate(segment),
        "is_silent": is_silent(segment)
    })

    # Frequency-domain features
    freqs, mag = compute_magnitude_spectrum(segment)
    result.update({
        "spectral_centroid": compute_spectral_centroid(freqs, mag),
        "normalized_magnitudes": mag / (np.max(mag) + EPSILON)
    })
    if timestamp >= ANALYSIS_WINDOW:
        prev_segment = get_segment_at_time(timestamp - ANALYSIS_WINDOW, ANALYSIS_WINDOW)
        if len(prev_segment) > 0:
            _, prev_mag = compute_magnitude_spectrum(prev_segment)
            result["spectral_flux"] = compute_spectral_flux(mag, prev_mag)
    
    # If global features are calculated
    if _global_calculated:
        # Beat detection features
        result.update({
            "is_beat": _is_beat(timestamp),
            "bpm": _audio_props["bpm"]
        })
        
        # Subband features (only if frequency analysis succeeded)
        raw_energies = _compute_subband_energies(freqs, mag)
        for band, energy in raw_energies.items():
            mean = _audio_props["subband_stats"]["means"][band]
            std = _audio_props["subband_stats"]["stds"][band]
            result[band] = np.tanh((energy - mean) / (std * 3))
    
    return result

# === UTILITY FUNCTIONS ========================================================
def compute_rms(audio: np.ndarray) -> float:
    return np.sqrt(np.mean(audio**2))

def compute_energy(audio: np.ndarray) -> float:
    return np.mean(audio**2)

def compute_zero_crossing_rate(audio: np.ndarray) -> float:
    return np.mean(np.abs(np.diff(np.sign(audio))))

def is_silent(audio: np.ndarray) -> bool:
    return compute_rms(audio) < SILENCE_THRESHOLD

def _is_beat(timestamp: float) -> bool:
    """Check if any beat occurs in current analysis window"""
    window_start = timestamp
    window_end = timestamp + ANALYSIS_WINDOW
    return any(window_start <= beat < window_end for beat in _audio_props["beats"])