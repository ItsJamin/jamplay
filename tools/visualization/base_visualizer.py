import os
import time
import threading
from config import Config
import scipy.io.wavfile as wav
from tools.analysis import analyze_segment

class BaseVisualizer:
    def __init__(self):
        self.song_name = None
        self.song_pos = 0.0
        self.song_playing = False
        self.song_timestamp = 0
        self.running = False

        self.thread = None
        self.elapsed_time = None

        self.music_file = None
        self.sample_rate = None

        self.width, self.height = 0, 0
        self.mapper = None
    
    def set_song_file(self):
        try: 
            path = os.path.join(Config.MUSIC_FOLDER, self.song_name + ".wav")
            self.sample_rate, self.music_file = wav.read(path)
        except:
            self.music_file = None
    
    def update(self, data_dict):
        """
        Updates the song metadata for visualization.
        """ 

        self.song_pos = float(data_dict["position"])
        self.song_playing = bool(data_dict["playing"])
        self.song_timestamp = time.time() 

        if self.song_name != str(data_dict["name"]):
            self.song_name = str(data_dict["name"])
            self.song_pos = 0.0  # Reset position when switching songs
            self.set_song_file()
    
    def start(self):
        """
        Starts the visualization in a separate thread.
        """
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.visualize, daemon=True)
            self.thread.start()
    
    def stop(self):
        """
        Stops the visualization.
        """
        self.running = False
        if self.thread:
            self.thread.join()
    
    def visualize(self):
        """
        Runs the visualization loop in a separate thread.
        """
        previous_segment = None  # Placeholder for audio segment caching
        
        while self.running:
            # Display song info
            if self.song_name:
                print(f"Now Playing: {self.song_name}")
                
                if self.song_playing:
                    self.elapsed_time = time.time() - (self.song_timestamp) + self.song_pos
                time_text = f"Time: {self.elapsed_time:.2f} sec"
                print(time_text)

                if self.music_file is not None:
                    # Extract current audio segment
                    audio_segment = self.music_file[int(self.elapsed_time * self.sample_rate):int((self.elapsed_time + 0.1) * self.sample_rate)]
                    # Perform analysis on the audio segment
                    analysis_data = analyze_segment(audio_segment, self.sample_rate)
                    print("Current Analysis Data:")
                    for key, value in analysis_data.items():
                        print(f"{key}: {value}")
            
            time.sleep(0.1)  # Avoid maxing out the CPU

