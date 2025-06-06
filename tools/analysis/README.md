# 🎧 Audio Analysis – Feature Description

This documentation explains all features extracted by the `analyze_segment` function, along with their meaning and value range.

## Important Notes:
- audio data is normalized to values between -1.0 and +1.0 to erase differences between different .wav files
- sample_rate/2 also known as Nyquist frequency is the highest frequency that can be encoded within a file with sample_rate. Therefore many of the features have something to do with sample_rate/2.

---

## Global Features
Global features are those that are calculated for the whole audio file once in the beginning.

### `is_beat`
`beats` are precalculated. `is_beat` is a boolean that states if a given segment has a beat in it. A beat is detected when a certain energy level is reached.

Value-Range: True or False

### `bpm`
Beats per Minute is a way of measuring the tempo of a song. This implementation should not be taken as accurate but more like a direction for the overall speed of the song. It is based on the calculated `beats` but with a filter - intervals less than 0.3 are not considered individual beats as this would suggest a bpm of 200 or higher (not usual).

Value-Range: 0 to 200
Typical values: 50 to 150

### `band_{freq_range}` (e.g. `band_bass`)
A (weighted) float that describes how strong the frequency range is relative to the whole Song. 

Value Range: -1.0 to +1.0 (could be higher but +-1 is 3 standard deviations from the mean)
Typical values: -0.7 to +0.7

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

### `is_silent`
Based on `rms` indicates if loudness is lower than a certain threshold.

### `spectral_flux`
The spectral flux measures how quickly the power changes.

Value-Range: 0 to Infinity
Typical Values: It is really depending on the music. Some music have hundreds as "normal amount of flux" and the thousands are only when the song is changing quickly. 


## Other

### `zero_crossing_rate`
How often a single segment of data crosses the zero-line. It is generally a quick indicator for a pitch of a signal.

Value-Range: 0 to 1
Typical Values: 0.05 to 0.5