import pygame
import time
from tools.visualization import BaseVisualizer
from tools.analysis import analyze_segment, get_audio_segment, normalize_amplitudes

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
        Main visualization loop using analyzed audio features only.
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
                    analysis = analyze_segment(audio_segment, self.sample_rate)
                    fft_magnitudes = analysis["fft"]
                    bar_heights = normalize_amplitudes(fft_magnitudes, max_height=200)

                    # Draw bars based on FFT
                    num_bars = len(bar_heights)
                    bar_width = self.screen.get_width() // num_bars
                    for i, height in enumerate(bar_heights):
                        pygame.draw.rect(
                            self.screen,
                            (0, 255, 0),
                            (
                                i * bar_width,
                                self.screen.get_height() - height,
                                bar_width - 2,
                                height
                            )
                        )

                    # Example: show energy or other info as text (optional)
                    energy = analysis["overall_energy"]
                    label = self.font.render(f"Energy: {energy:.2f}", True, (255, 255, 255))
                    self.screen.blit(label, (10, 10))

                except Exception as e:
                    print("Visualization error:", e)

            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()
