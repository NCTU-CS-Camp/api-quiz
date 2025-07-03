from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from flask_socketio import SocketIO
# from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address

db   = SQLAlchemy()
auth = HTTPBasicAuth()
socketio = SocketIO(cors_allowed_origins="*")
# limiter = Limiter(key_func=get_remote_address, default_limits=["100 per minute"])
