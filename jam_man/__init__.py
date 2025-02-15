from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
import redis

app = Flask(__name__, template_folder='../frontend/templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../resources/database.db'

# Initialisierung von Modulen
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# 🔥 Hier API importieren, damit die Routen geladen werden!
from jam_man import api
