# JamMan

JamMan is a Music Manager for your home network which you can acces from any device in this network. The main function of JamMan is the managing role between JamVis and JamPlay. JamPlay can be used to play music, while JamVis allows the music to be visualised with LEDs or another medium.

The goal is to have a RaspberryPi as a single device to use as your Music Manager.

# Project Structure and Flow

## Structure
```
jam-man
- front-end
- back-end
- connecting component to jam-play
- download with link (using yt-dlp)
- database with songs and meta-data
jam-play
- play the music (onto audio device)
- interact with interface to jam-vis to update visual device (if wanted)
jam-vis
- analyze the music
- give back vizualization for given time in interface
```

## Flow
1. Open Front-End (Website)
- Display available songs via jam-man or download songs via jam-get
2. Choose a song
- jam-man takes choice, gives it to jam-play
- jam-play then gives it jam-vis for analyzing
- while playing the song jam-play communicates with jam-vis to get visualization-data

