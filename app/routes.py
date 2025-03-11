from flask import Blueprint, jsonify, request, render_template, send_from_directory
import os
from yt_dlp import YoutubeDL
from config import Config
import time
import subprocess
from threading import Thread, Lock

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/api/play/')
def play_song():
    song = request.args.get('song')
    print(song)
    return send_from_directory(Config.MUSIC_FOLDER, _get_filename(song))

@bp.route('/api/songs/')
def list_songs():
    query = request.args.get('q').lower()
    songs = []
    for f in os.listdir(Config.MUSIC_FOLDER):
        if f.endswith(Config.ALLOWED_EXTENSION):
            clean_name = os.path.splitext(f)[0]
            if query in clean_name.lower() and query.strip() != "":
                songs.append({
                    'name': clean_name,
                })
    return jsonify(songs)

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
                original_filename = f"{info['title']}.wav"
                
                if data['rename'] and len(data['rename']) > 0:
                    safe_rename = "".join(c for c in data['rename'] if c.isalnum() or c in (" ", "_", "-")).rstrip()
                    new_filename = f"{safe_rename}.wav"
                else:
                    new_filename = original_filename

                original_path = os.path.join(Config.MUSIC_FOLDER, original_filename)
                target_path = os.path.join(Config.MUSIC_FOLDER, new_filename)

                # Check that it is a new song before downloading
                if os.path.exists(target_path):
                    return jsonify({'error': 'Already a song in library with this name'})
                
                info = ydl.extract_info(url, download=True)

                if os.path.exists(original_path):
                    os.rename(original_path, target_path)

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
    data = request.json
    print(data)
    return jsonify({'success': True})



# Help Functions

def _get_filename(song : str) -> str:
    return song if song.endswith(".wav") else song + ".wav"

def _get_songtitle(song : str) -> str:
    return song if not song.endswith(".wav") else song[:-4]