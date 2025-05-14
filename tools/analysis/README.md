# 🎧 Audio Analysis – Feature Description

This documentation explains all features extracted by the `analyze_segment` function, along with their meaning and value range.

## Important Notes:
- audio data is normalized to values between -1.0 and +1.0 to erase differences between different .wav files
- sample_rate/2 also known as Nyquist frequency is the highest frequency that can be encoded within a file with sample_rate. Therefore many of the features have something to do with sample_rate/2.

---

## Frequency-Based Features

### `spectral_centroid`
The spectral centroid indicates where center of mass is in a spectrum. It gives a good impression of the brightness of a sound.

Value-Range: 0hz to sample_rate/2hz
Typical values: high hundreds to a few thousands

### `normalized_magnitudes`
Is an array of the magnitude of all frequencies *relative to the other frequency in that time point*.
The dominant frequency is therefore 1. It is a good measure to see which frequencies are dominant but not for comparisons to other time points because of this relativeness.

Value-Range: Array of length sample_rate/2 with values between 0 and 1.

## Time/Dynamics Features

### `rms`
RMS or "Root Mean Square" is used to measure continuous power output of an audio signal.
It gives the average energy in a timeframe and is a good indicator for perceived loudness, because it outliers are averaged with the rest.

Value-Range: -1.0 to +1.0
Typical Values: 0.05 to 0.5

### `spectral_flux`
The spectral flux measures how quickly the power changes.

Value-Range: 0 to Infinity
Typical Values: It is really depending on the music. Some music have hundreds as "normal amount of flux" and the thousands are only when the song is changing quickly. 