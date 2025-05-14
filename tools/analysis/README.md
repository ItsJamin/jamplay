# 🎧 Audio Analysis – Feature Description

This documentation explains all features extracted by the `analyze_segment` function, along with their meaning and value range.

## Important Notes:
Audio Data is normalized to values between -1.0 and +1.0.
The Value-Ranges are therefore based on normalized data.

---

## Frequency-Based Features

### `spectral_centroid`
The spectral centroid indicates where center of mass is in a spectrum. It gives a good impression of the brightness of a sound.

Value-Range: 0hz to sample_rate/2hz
Typical values: high hundreds to a few thousands

## Time/Dynamics Features

### `rms`
RMS or "Root Mean Square" is used to measure continuous power output of an audio signal.
It gives the average energy in a timeframe and is a good indicator for perceived loudness, because it outliers are averaged with the rest.

Value-Range: -1.0 to +1.0
Typical Values: 0.05 to 0.5

