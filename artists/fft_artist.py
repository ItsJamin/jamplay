import numpy as np

class FFTArtist:
    """Generates a RELATIVE 2D visualization of the frequency spectrum with fading effect."""

    def __init__(self, audio_processor, height=10, width=100):
        """
        Initializes the artist.
        
        Parameters:
            audio_processor: The AudioProcessor instance to retrieve data from.
            height (int): Number of vertical pixels.
            width (int): Number of horizontal pixels (matches FFT bins).
        """
        self.audio_processor = audio_processor  # Artist gets direct access to audio data
        self.height = height
        self.width = width
        self.last_image = np.zeros((height, width, 3), dtype=np.uint8)  # Store last frame

    def create_relative_visualization(self, position):
        """
        Fetches FFT data from the AudioProcessor and generates a relative 2D visualization.
        The previous frame is blended in with 20% transparency.

        Parameters:
            position (float): The current playback position in seconds.

        Returns:
            np.ndarray: A (height, width, 3) array representing the relative color distribution.
        """
        # Get the FFT magnitudes for the given position
        fft_magnitudes = self.audio_processor.get_fft_for_time(position)
        
        # Ensure width consistency
        fft_magnitudes = fft_magnitudes[:self.width]
        fft_magnitudes /= np.max(fft_magnitudes) if np.max(fft_magnitudes) > 0 else fft_magnitudes

        # Create a new 2D relative visualization
        new_image = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        for y in range(self.height):
            for x in range(self.width):
                intensity = fft_magnitudes[x] * (1 - y / self.height)  # Top brighter, bottom darker
                new_image[y, x] = [intensity * 255, 255 - (intensity * 255), 100]  # RGB

        # Blend with the previous frame (80% new, 20% old for fading effect)
        blended_image = (0.1 * new_image + 0.9 * self.last_image).astype(np.uint8)

        # Store the new frame for the next iteration
        self.last_image = blended_image.copy()

        return blended_image
