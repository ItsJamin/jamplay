from tools.visualization import BaseVisualizer
from tools.analysis import analyze_segment, set_audio
from tools.mapping import *
import time
import neopixel
import board

class LEDVisualizer(BaseVisualizer):
    def __init__(self, led_count, _, mapper_cls=BaseMapper):
        super().__init__()

        self.led_count = led_count
        self.mapper = mapper_cls(led_count, 1)
        self.led_strip = neopixel.NeoPixel(board.D18, self.led_count, auto_write = False)
        self.led_strip.fill((0, 0, 0))
        self.led_strip.show()
        
    
    def visualize(self):
        while self.running:
            
            self.led_strip.fill((0, 0, 0))
            
            
            if self.song_name and self.song_playing and self.music_file is not None:
                self.elapsed_time = time.time() - (self.song_timestamp) + self.song_pos + 0.1

                try:
                    analysis = analyze_segment(self.elapsed_time)
                    if self.mapper:
                        color_line = self.mapper.map(analysis)[0]  # -> RGB 2D array (height x 1)

                        self.led_strip[0:len(color_line)-1] = color_line[0:len(color_line)-1]
                except Exception as e:
                    print(e)
            
            self.led_strip.show()
        
        self.led_strip.fill((0, 0, 0))
        self.led_strip.show()


