import pygame
import time
from tools.visualization import BaseVisualizer
from tools.analysis import analyze_segment, get_audio_segment, normalize_amplitudes
from tools.mapping import BaseMapper, BasicFFTMapper
import numpy as np

class PygameVisualizer(BaseVisualizer):
    def __init__(self, width, height, mapper_cls=BasicFFTMapper):
        super().__init__()

        self.width = width
        self.height = height
        self.mapper = mapper_cls(width, height)

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
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

            if self.song_name and self.song_playing and self.music_file is not None:
                self.elapsed_time = time.time() - self.song_timestamp + self.song_pos
                audio_segment = get_audio_segment(self.music_file, self.sample_rate, self.elapsed_time)

                try:
                    analysis = analyze_segment(audio_segment, self.sample_rate)
                    if self.mapper:
                        frame_array = self.mapper.map(analysis)  # -> RGB 2D array (height x width x 3)

                        surface = pygame.surfarray.make_surface(np.transpose(frame_array, (1, 0, 2)))
                        self.screen.blit(surface, (0, 0))

                except Exception as e:
                    print(f"Visualizer error: {e}")

            pygame.display.flip()
            self.clock.tick(30)


        pygame.quit()