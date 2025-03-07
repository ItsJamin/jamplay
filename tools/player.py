
queue = []
"""
Important notes:
- queue stores with file-ending
- front-end only gets to see without file-ending
"""


def add_to_queue(name : str):
    """Adds a song to the queue"""
    queue.append(_get_filename(name))

def play_song(name : str):
    """Gets the name for the next Song to be played and removes it from queue"""
    if len(queue) == 0 or queue[0] != _get_filename(name):
        return ""
    return  _get_songtitle(queue.pop(0))

def get_queue():
    """Returns the queue in order"""
    return [_get_songtitle(q) for q in queue]

# Help Functions

def _get_filename(song : str) -> str:
    return song if song.endswith(".wav") else song + ".wav"

def _get_songtitle(song : str) -> str:
    return song if not song.endswith(".wav") else song[:-4]