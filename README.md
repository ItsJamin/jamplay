# JamVis
An interface for calculating good-looking audio-visualizations.
One of a two-part-project, the other one (JamMan) being the actual manager between audiosource, JamVis and hardware components such as LEDs and/or speakers.

Visualization is pre-calculated (not a stream of audio, rather a file). This may not be as flexible but it allows for more in-depth analysis of music data.

# The Flow

## Input

First you'll need to set the dimensions (width and length). After that you'll need to provide an .wav file.

## Artists

Choose on what features and in which ways the music should be visualized (choose an artist).

## Mapper

Mapper take the results from artists and map them onto the given dimensions.

## Output

A frame_generator (iterator over frames) where each frame is an pixel-array with colors in the wanted dimensions. Frames are one sample_rate long.

