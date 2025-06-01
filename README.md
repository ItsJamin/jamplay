# JamPlay 0.0.1

JamPlay is intended to be a framework for playing music while visualizing the music. The basic idea is that playing the music and visualizing the music is seperated from another (several reasons one of them being linux).

## Example, Pros and Cons
The user opens the website on their smartphone and starts playing a song. The backend, in this example a RaspberryPi, analyses the music and visualizes it with an LED-Strip.
(But it could just be used as local music player.)

What are the benefits?
+ input is very user-friendly because it isn't dependend on a single or specific device and the output (e.g. a bluetooth box) is easily connected.
+ you don't get problems with linux alsa audio driver sh*t
+ you don't get problems with linux sudo rights (e.g. one library which only works in sudo and another one that only works without sudo)
+ (you don't get problems with librosa dependencies because the feature-analysis is selfmade)

What is suboptimal?
- minor latencies in synchronisation (should not be an issue in the end)
- Website as the player is a little bit awkward and access-concept is needed so that not multiple people play music, because website is not suited for synchronisation of multiple users.

# Setup JamPlay

1. Clone the repository `git clone https://github.com/ItsJamin/jamplay.git`

2. Create and activate a virtual environment und install the packages in it.
```
cd jamplay
python -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

If you also want to use the LED Visualization, you have to install these (only tested for Raspberry Pi 4):
```
pip3 install rpi_ws281x
pip3 install adafruit-circuitpython-neopixel
python3 -m pip install --force-reinstall adafruit-blinka
```

3. Configurate your program
In the `config.py` you can set up variables such as which visualizer to use or yt-dlp Options.
NOTE: If you are using the LED Visualizer, the GPIO PIN is not configured in the `config.py` but in the `led_visualizer.py`.

4. Local Network Access
If you want to access this player from your local network, you have to open the port for the firewall on your local server. You can use the `open_port.sh` for this as follows:
`chmod +x open_port.sh`
`./open_port.sh`

Now you can get your local ip-address with the `ipconfig` command such and connect to it which looks something like this `192.168.172.XX:5050`.

# Components

## JamPlayer
The music player is a website that can be used for playing, queueing or adding songs to your library.

## The BackEnd
The backend of the website serves as an organizer, download-handler and gives the search results of the local library.
The backend is also responsible for keeping the visualizer on the BackEnd Device and the music on the FrontEnd synced.

## JamVisualizer
The visualizer should visualize the music. There are three main steps to this:
- Analyze: Analyses the music and gives back the features
- Mapper: How the features are *presented* ("What should be on the canvas?"), e.g. beats should make the screen red.
- Visualizer: How the features are *displayed* ("What is the canvas?"), e.g. visualizing through a pygame window or visualizing through an external LED-strip.

## Planned

- A good mapper that is not just a one-trick-pony and actually creates interesting visualizations from the features.
- Website improvements:
    - only one user at the time as a player (the other one can maybe queue or suggest songs)
    - when searching for a song enter should directly add to queue
- more features would be nice
