from jam_man import app, socketio
from jam_man.db import init_db

if __name__ == '__main__':
    #init_db()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
