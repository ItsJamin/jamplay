from jam_man import redis_client
from jam_man.db import Song
from flask import jsonify

def add_to_queue(song_id):
    song = Song.query.get(song_id)
    if not song:
        return jsonify({'error': 'Song not found'}), 404
    redis_client.rpush('song_queue', song.file_path)
    return jsonify({'message': 'Song added to queue'})

def get_next_song():
    next_song = redis_client.lpop('song_queue')
    if next_song:
        return jsonify({'next_song': next_song.decode('utf-8')})
    return jsonify({'message': 'Queue is empty'})
