import os

class Config:
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