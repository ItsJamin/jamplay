import pygame
import time
from tools.visualization import BaseVisualizer
from tools.analysis import analyze_segment, set_audio
from tools.mapping import *
import numpy as np

class PygameVisualizer(BaseVisualizer):
    def __init__(self, width, height, mapper_cls=BaseMapper):
        super().__init__()

        self.width = width
        self.height = height
        self.mapper = mapper_cls(width, height)

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("Music Visualizer")
        self.font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()

    def visualize(self):
        while self.running:
            self.screen.fill((0, 0, 0))  # Clear screen

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()
                    return
                elif event.type == pygame.VIDEORESIZE:
                    self.width, self.height = event.size
                    self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)

            if self.song_name and self.song_playing and self.music_file is not None:
                self.elapsed_time = time.time() - (self.song_timestamp) + self.song_pos + 0.1

                try:
                    analysis = analyze_segment(self.elapsed_time)
                    if self.mapper:
                        frame_array = self.mapper.map(analysis)  # -> RGB 2D array (height x width x 3)
                        surface = pygame.surfarray.make_surface(np.transpose(frame_array, (1, 0, 2)))
                        scaled_surface = pygame.transform.scale(surface, self.screen.get_size())
                        self.screen.blit(scaled_surface, (0, 0))
                except Exception as e:
                    print(e)

            pygame.display.flip()
            self.clock.tick(30)


        pygame.quit()