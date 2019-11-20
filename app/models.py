from datetime import datetime
from app import login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from time import time
import jwt
from flask import current_app
from app import db


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    tips = db.relationship('Tip', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except Exception as e:
            current_app.logger.error('Error')
            return
        return User.query.get(id)


hashtags = db.Table('hashtags_tips',
                    db.Column('hashtags_id', db.Integer, db.ForeignKey('hashtags.id'), primary_key=True),
                    db.Column('tips_id', db.Integer, db.ForeignKey('tips.id'), primary_key=True))


class Tip(db.Model):
    __tablename__ = 'tips'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    hashtags = db.relationship('HashTag', secondary=hashtags, lazy='subquery', backref=db.backref('tips', lazy=True))

    def __repr__(self):
        return self.body


class HashTag(db.Model):
    __tablename__ = 'hashtags'
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(64))

    def __repr__(self):
        return self.tag

#examples
# h = Tip.query.join(hashtags).filter_by(tips_id=14).all()
# return Tip

#>>> h = HashTag.query.join(hashtags).filter_by(tips_id=14).all()
#>>> h
#[]
# return HashTag by tip
#>>> h = HashTag.query.join(hashtags).all()