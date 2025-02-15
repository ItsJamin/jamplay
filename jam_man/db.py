from jam_man import db

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)

def init_db():
    with db.app.app_context():
        db.create_all()
