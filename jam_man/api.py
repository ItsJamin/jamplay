from flask import request, jsonify, render_template
from jam_man import app, db
from jam_man.db import Song
from jam_man.queue import add_to_queue, get_next_song
import yt_dlp
import os

RESOURCES_PATH = "../resources/songs/"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/songs', methods=['GET'])
def get_songs():
    songs = Song.query.all()
    return jsonify([{ 'id': s.id, 'title': s.title, 'artist': s.artist } for s in songs])

@app.route('/queue/add', methods=['POST'])
def queue_song():
    data = request.json
    song_id = data.get('song_id')
    return add_to_queue(song_id)

@app.route('/queue/next', methods=['GET'])
def next_song():
    return get_next_song()

@app.route('/songs/upload', methods=['POST'])
def upload_song():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    
    # yt-dlp Konfiguration
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': RESOURCES_PATH + '%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info_dict)
        subpath = os.path.relpath(filename, RESOURCES_PATH)
    
    # Song in die Datenbank einfügen
    new_song = Song(title=info_dict['title'], artist=info_dict.get('uploader', 'Unknown'), file_path=subpath)
    db.session.add(new_song)
    db.session.commit()
    
    return jsonify({"message": "Song uploaded successfully", "file_path": subpath})