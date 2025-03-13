import pygame
import os
import time
import threading
from config import Config

class Visualizer:
    def __init__(self):
        self.song_name = None
        self.song_pos = 0.0
        self.song_playing = False
        self.song_timestamp = 0
        
        pygame.init()
        self.screen = pygame.display.set_mode((400, 200))
        pygame.display.set_caption("Music Visualizer")
        self.font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()
        self.running = False
        self.thread = None
    
    def get_song_file(self):
        try: 
            path = os.path.join(Config.MUSIC_FOLDER, self.song_name + ".wav")
            return path if os.path.exists(path) else None
        except:
            return None
    
    def update(self, data_dict):
        """
        Updates the song metadata for visualization.
        """ 

        time_point_reference = data_dict["time"]
        backend_at_time_point_reference = (time_point_reference/1000) - (self.song_timestamp / 1000) + self.song_pos
        print(f"""UPDATE FEEDBACK: 
              Point of Time: {time_point_reference}
                - Where it should be: {data_dict["position"]}
                - Where it is: {backend_at_time_point_reference}
                - Difference of: {abs(data_dict["position"]-backend_at_time_point_reference)}
              """)

        self.song_pos = float(data_dict["position"])
        self.song_playing = bool(data_dict["playing"])
        self.song_timestamp = time.time() 
        # SHOULD: int(data_dict["time"])
        # Timestamp reference is somehow worse, maybe because of fingerprinting defense mechanisms

        if self.song_name != str(data_dict["name"]):
            self.song_name = str(data_dict["name"])
            self.song_pos = 0.0  # Reset position when switching songs
    
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
        while self.running:
            self.screen.fill((0, 0, 0))  # Clear screen
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()
                    return
                    
            # Display song info
            if self.song_name:
                text = self.font.render(f"Now Playing: {self.song_name}", True, (255, 255, 255))
                self.screen.blit(text, (20, 50))
                
                if self.song_playing:
                    elapsed_time = time.time() - (self.song_timestamp) + self.song_pos
                time_text = self.font.render(f"Time: {elapsed_time:.2f} sec", True, (255, 255, 255))
                self.screen.blit(time_text, (20, 100))
            
            pygame.display.flip()
            self.clock.tick(30)  # Limit frame rate to 30 FPS
        
        pygame.quit()
