from flask_socketio import SocketIO

socket = None


def init_socketio(app):
    global socket
    socket = SocketIO(app)


def get_socketio():
    return socket
