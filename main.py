from core.player import Player
from core.audio_processor import AudioProcessor
from artists.fft_artist import FFTArtist
from mappers.proportional_mapper import ProportionalMapper
from visualizer.display import PygameDisplay

if __name__ == "__main__":
    file = "assets/test.wav"

    # Initialize components
    audio_processor = AudioProcessor(file)
    artist = FFTArtist(audio_processor)
    mapper = ProportionalMapper(width=10, height=5)

    # Use Pygame display
    display = PygameDisplay(width=10, height=5, pixel_size=100)

    # Initialize and start the player
    player = Player(file, artist, mapper, display)
    player.play_and_visualize()

    # Close display when finished
    display.close()
