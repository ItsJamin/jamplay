# 🎧 Audio Analysis – Feature Description

This documentation explains all features extracted by the `analyze_segment` function, along with their meaning and potential use in visualization.

---

## Frequency-Based Features

### `bass_level`
- **Description**: Average energy in frequencies below 250 Hz.
- **Usage**: Represents low-end energy (e.g., kick drums, bass lines); ideal for ground-shaking, pulsing visuals.

### `mid_level`
- **Description**: Average energy between 250 Hz and 1000 Hz.
- **Usage**: Captures midrange frequencies (e.g., vocals, guitars); useful for expressive or organic visuals.

### `treble_level`
- **Description**: Average energy above 1000 Hz.
- **Usage**: Highlights high-end content (e.g., hi-hats, snares); great for sparkling, delicate particles or sharp lines.

### `bass_ratio`, `mid_ratio`, `treble_ratio`
- **Description**: Proportion of total energy found in each frequency range.
- **Usage**: Enables balance-aware visual adjustments like color weighting or frequency-based layout.

### `melody_energy`
- **Description**: Energy within the 100–2000 Hz range.
- **Usage**: Often includes melodic instruments – great for leading shapes or prominent layers.

### `high_freq_energy`
- **Description**: Energy in the high-frequency range (>2000 Hz).
- **Usage**: Drives fine detail and brightness in visual effects.

---

## Time/Dynamics Features

### `rms`
- **Description**: Root Mean Square – average signal energy.
- **Usage**: Simple loudness metric – good for particle speed, size, or count.

### `loudness`
- **Description**: Decibel-based estimate of signal power (`20 * log10(rms)`).
- **Usage**: More realistic loudness perception – helpful for scaling visuals intuitively.

### `dynamic_range`
- **Description**: Difference between max and min amplitude in the segment.
- **Usage**: Indicates the "punchiness" or softness of the sound – useful for contrast in visuals.

### `zero_crossing_rate` (ZCR)
- **Description**: Rate of sign changes in the waveform.
- **Usage**: High ZCR = noise or percussive content – great for glitchy or rough visual elements.

---

## Spectral Features

### `spectral_centroid`
- **Description**: The “center of mass” of the frequency spectrum – higher = brighter sound.
- **Usage**: Can modulate color temperature or position to reflect perceived brightness.

### `spectral_bandwidth`
- **Description**: Spread of the frequency spectrum.
- **Usage**: Expresses the richness of sound – useful for adding spatial complexity.

### `spectral_flux`
- **Description**: Change in spectrum compared to the previous frame.
- **Usage**: Detects transitions or movement in audio – great for bursts or switching animations.

### `spectral_contrast`
- **Description**: Standard deviation of the normalized FFT spectrum.
- **Usage**: Indicates variation across frequencies – useful for visual "texture" or granularity.

---

## Rhythm & Transient Features

### `energy_change`
- **Description**: Difference in overall energy from the previous frame.
- **Usage**: Useful for creating reactive spikes or buildup effects.

### `is_beat`
- **Description**: True if spectral flux is significantly above recent average.
- **Usage**: Beat detection – key for syncing visuals rhythmically.

### `attack`
- **Description**: Difference between flux and ZCR – measures transient sharpness.
- **Usage**: Detects strong onset events – ideal for triggering snappy visual changes.

---

## Meta Features

### `overall_energy`
- **Description**: Average energy across the FFT spectrum.
- **Usage**: General measure of activity – good for controlling density, intensity, or motion.

### `fft`
- **Description**: Normalized, log-scaled FFT spectrum.
- **Usage**: Base data for frequency visualizers like bars, shapes, or frequency grids.

### `tempo_estimate`
- **Description**: (Placeholder for future tempo detection)
- **Usage**: Can eventually be used for BPM-based synchronization.

### `is_silent`
- **Description**: True if RMS is below a certain threshold.
- **Usage**: Useful for fading visuals or indicating pauses.
