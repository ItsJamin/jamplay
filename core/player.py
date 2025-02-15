import pygame
from core.audio_processor import AudioProcessor

class Player:
    """Handles music playback and synchronizes visualization."""

    def __init__(self, file, artist, mapper, display):
        """
        Initializes the player.
        
        Parameters:
            file (str): Path to the audio file.
            artist (Artist): Artist instance for visualization.
            mapper (Mapper): Mapper instance for pixel conversion.
            display (Display): Display instance for rendering.
        """
        self.audio_processor = AudioProcessor(file)
        self.artist = artist
        self.mapper = mapper
        self.display = display  # Now passed externally

        pygame.mixer.pre_init(frequency=self.audio_processor.sr)
        pygame.mixer.init()#(48000, -16, 1, 1024)
        pygame.mixer.music.load(file)

    def play_and_visualize(self):
        """Plays the audio and updates the visualization in real-time."""
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            position = pygame.mixer.music.get_pos() / 1000  # Current playback position

            # Artist retrieves its own data from the AudioProcessor
            relative_image = self.artist.create_relative_visualization(position)

            # Mapper converts relative image to actual pixel format
            frame = self.mapper.map(relative_image)

            # Send frame to the external display
            self.display.show_frame(frame)

