import os
from tools.mapping import *
from tools.visualization import *

class Config:
    # VISUALIZER OPTIONS #

    MAPPER_CLASS = ScrollingMapper
    VISUALIZER_CLASS = PygameVisualizer
    WIDTH = 1500
    HEIGHT = 300

    # DOWNLOAD OPTIONS #
    MUSIC_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'music')
    ALLOWED_EXTENSION = '.wav'
    SECRET_KEY = 'jampla-sctkey'
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'outtmpl': 'music/___temp.%(ext)s',
    }
    FORBIDDEN_CHARS_IN_NAME = ["~", "“", "#", "%", "&", "*" ,":", "<", ">" ,"?", "/", "\\", "{", "|", "}"]
