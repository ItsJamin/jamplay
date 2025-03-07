from flask import Flask
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    from app.routes import bp
    app.register_blueprint(bp)

    if not os.path.exists(app.config['MUSIC_FOLDER']):
        os.makedirs(app.config['MUSIC_FOLDER'])
    
    return app