from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    team          = db.Column(db.Integer, default=0)
    iq            = db.Column(db.Integer, default=0)

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)
    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'team': self.team,
            'iq': self.iq
        }
