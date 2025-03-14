import pygame
import os
import time
from tools.visualization import BaseVisualizer
from tools.analysis import compute_fft, get_audio_segment, normalize_amplitudes

class PygameVisualizer(BaseVisualizer):
    def __init__(self):
        super().__init__()
        
        pygame.init()
        self.screen = pygame.display.set_mode((400, 200))
        pygame.display.set_caption("Music Visualizer")
        self.font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()
    
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

            if self.song_name and self.song_playing and self.music_file is not None:
                self.elapsed_time = time.time() - self.song_timestamp + self.song_pos
                audio_segment = get_audio_segment(self.music_file, self.sample_rate, self.elapsed_time)
                
                try:
                    magnitudes = compute_fft(audio_segment, self.sample_rate)
                    bar_heights = normalize_amplitudes(magnitudes, max_height=200)

                    # Zeichne die Balken
                    num_bars = len(bar_heights)
                    bar_width = self.screen.get_width() // num_bars
                    for i, height in enumerate(bar_heights):
                        pygame.draw.rect(self.screen, (0, 255, 0), 
                                        (i * bar_width, self.screen.get_height() - height, 
                                        bar_width - 2, height))
                except:
                    pass

            pygame.display.flip()
            self.clock.tick(30)  # Limit frame rate to 30 FPS
        
        pygame.quit()
