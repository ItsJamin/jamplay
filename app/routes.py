from flask import Blueprint, jsonify, request, render_template, send_from_directory
import os
from yt_dlp import YoutubeDL
from config import Config
import time
import subprocess
from threading import Thread, Lock
from tools.visualization import PygameVisualizer, BaseVisualizer

bp = Blueprint('main', __name__)

db = [os.path.splitext(f)[0] for f in os.listdir(Config.MUSIC_FOLDER) if f.endswith(Config.ALLOWED_EXTENSION)]

vis = PygameVisualizer()
vis.start()

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/api/play/')
def play_song():
    song = request.args.get('song')
    return send_from_directory(Config.MUSIC_FOLDER, _get_filename(song))

@bp.route('/api/songs/')
def list_songs():
    query = request.args.get('q', '').strip().lower()

    matching_songs = [f for f in db if query in f.lower()]
    sorted_songs = sorted(matching_songs, key=lambda f: (f.lower().find(query), f.lower()))

    return jsonify(sorted_songs)


@bp.route('/api/queue', methods=['POST'])
def validate_song():
    data = request.json
    if 'url' in data:
        url = data['url'].strip().split('&')[0]
        if not url:
            return jsonify({'error': 'Empty URL'}), 400
        
        try:
            with YoutubeDL(Config.YTDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                original_filename = f"___temp.wav"
                
                if data['rename'] and len(data['rename']) > 0:
                    safe_rename = "".join(c for c in data['rename'] if not c in Config.FORBIDDEN_CHARS_IN_NAME).rstrip()
                else:
                    safe_rename = "".join(c for c in info['title'] if not c in Config.FORBIDDEN_CHARS_IN_NAME).rstrip()
                new_filename = f"{safe_rename}.wav"

                original_path = os.path.join(Config.MUSIC_FOLDER, original_filename)
                target_path = os.path.join(Config.MUSIC_FOLDER, new_filename)
                # Check that it is a new song before downloading
                if os.path.exists(target_path):
                    return jsonify({'error': 'Already a song in library with this name'})
                
                info = ydl.extract_info(url, download=True)

                if os.path.exists(original_path):
                    os.rename(original_path, target_path)

                db.append(_get_songtitle(new_filename))

                return jsonify({'success': True, 'name': _get_songtitle(new_filename)})
        
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    else:
        song = data.get('song', '').strip()
        if not song:
            return jsonify({'error': 'Empty song name'}), 400
        
        if not os.path.exists(os.path.join(Config.MUSIC_FOLDER, song)):
            return jsonify({'error': 'Song not in library'}), 404
        
        # player.add_to_queue(song)
        return jsonify({'success': True, 'name': _get_songtitle(song)})


@bp.route('/api/player/status', methods=['POST'])
def set_info():
    """
    Gets Data in a specific format:
    - playing: true/false
    - time: when action was executed
    - name: name of song
    - position: position in song
    """
    data = request.json
    vis.update(data)
    return jsonify({'success': True})


@bp.route('/api/player/status', methods=['GET'])
def get_info():
    vis.song_playing = False
    return jsonify({
        'name': vis.song_name,
        'time': vis.elapsed_time,
        'playing': vis.song_playing,
        'success': True
    })

# Help Functions

def _get_filename(song : str) -> str:
    return song if song.endswith(".wav") else song + ".wav"

def _get_songtitle(song : str) -> str:
    return song if not song.endswith(".wav") else song[:-4]