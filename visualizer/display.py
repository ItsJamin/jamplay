import pygame
import numpy as np

class PygameDisplay:
    """Handles visualization using Pygame."""

    def __init__(self, width, height, pixel_size=10):
        """
        Initializes the Pygame window.

        Parameters:
            width (int): Number of pixels in width.
            height (int): Number of pixels in height.
            pixel_size (int): Size of each pixel in the display.
        """
        self.width = width
        self.height = height
        self.pixel_size = pixel_size  # Controls how large each "pixel" appears on screen

        pygame.init()
        self.screen = pygame.display.set_mode((width * pixel_size, height * pixel_size))
        pygame.display.set_caption("JamVis Visualizer")
        self.clock = pygame.time.Clock()

    def show_frame(self, frame):
        """
        Renders a new frame.

        Parameters:
            frame (np.ndarray): A (height, width, 3) array representing the colors.
        """
        for y in range(self.height):
            for x in range(self.width):
                color = frame[y, x]  # Get RGB values from the frame
                pygame.draw.rect(
                    self.screen,
                    color,
                    (x * self.pixel_size, y * self.pixel_size, self.pixel_size, self.pixel_size),
                )

        pygame.display.flip()
        #self.clock.tick(60)  # Keep frame rate at ~60 FPS

    def close(self):
        """Closes the Pygame window."""
        pygame.quit()
