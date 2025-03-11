from flask import Blueprint, jsonify, request, render_template, send_from_directory
import os
from yt_dlp import YoutubeDL
from config import Config
import time
import subprocess
from threading import Thread, Lock
import tools.player as player

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/api/play/')
def play_song():
    song = request.args.get('song')
    player.play_song(song)
    return send_from_directory(Config.MUSIC_FOLDER, player._get_filename(song))

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
    print(songs)
    return jsonify(songs)

@bp.route('/api/queue', methods=['POST'])
def add_to_queue():
    data = request.json
    if 'url' in data:
        url = data['url'].strip().split('&')[0]
        if not url:
            return jsonify({'error': 'Empty URL'}), 400
        
        try:
            with YoutubeDL(Config.YTDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = f"{info['title']}.wav"
                target_path = os.path.join(Config.MUSIC_FOLDER, filename)
                
                if not os.path.exists(target_path):
                    os.rename(f"{info['title']}.wav", target_path)
                
                player.add_to_queue(filename)
                return jsonify({'success': True})
        
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    else:
        song = data.get('song', '').strip()
        if not song:
            return jsonify({'error': 'Empty song name'}), 400
        
        if not os.path.exists(os.path.join(Config.MUSIC_FOLDER, song)):
            return jsonify({'error': 'File not found'}), 404
        
        player.add_to_queue(song)
        return jsonify({'success': True})

@bp.route('/api/queue', methods=['GET'])
def get_queue():
    queue = player.get_queue()
    return jsonify([{
        'name': song
    } for song in queue])


@bp.route('/api/player/status', methods=['POST'])
def set_info():
    data = request.json
    print(data)
    return jsonify({'success': True})