from jam_man import db

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200), nullable=True)
    album = db.Column(db.String(200), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    file_path = db.Column(db.String(200), nullable=False)

def init_db():
    with db.app.app_context():
        db.create_all()
