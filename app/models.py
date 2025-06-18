from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    team          = db.Column(db.Integer, default=0)
    iq            = db.Column(db.Integer, default=90)
    
    # add relationship
    answers = db.relationship('UserAnswer', backref='user', cascade='all, delete-orphan')


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

class UserAnswer(db.Model):
    __tablename__ = 'user_answers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, nullable=False)
    # answered_at = db.Column(db.DateTime, server_default=db.func.now())

    __table_args__ = (
        db.UniqueConstraint('user_id', 'question_id', name='_user_question_uc'),
    )