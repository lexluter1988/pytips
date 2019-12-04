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


hashtags = db.Table('hashtags_tips',
                    db.Column('hashtags_id', db.Integer, db.ForeignKey('hashtags.id'), primary_key=True),
                    db.Column('tips_id', db.Integer, db.ForeignKey('tips.id'), primary_key=True))

followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('users.id')))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    confirmed = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    tips = db.relationship('Tip', backref='author', lazy='dynamic')

    followed = db.relationship('User', secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_token(self, expires_in=600, token_type='reset_password'):
        return jwt.encode(
            {token_type: self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_token(token, token_type='reset_password'):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])[token_type]
        except Exception as e:
            current_app.logger.error('Error {}'.format(e))
            return
        return User.query.get(id)


class Tip(db.Model):
    __tablename__ = 'tips'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    hashtags = db.relationship('HashTag', secondary=hashtags, lazy='subquery', backref=db.backref('tips', lazy=True))
    likes = db.relationship('Like', backref='likes', lazy='dynamic')

    def __repr__(self):
        return self.body


class HashTag(db.Model):
    __tablename__ = 'hashtags'
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(64))

    def __repr__(self):
        return self.tag


class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    tip_id = db.Column(db.Integer, db.ForeignKey('tips.id'))


# examples
# h = Tip.query.join(hashtags).filter_by(tips_id=14).all()
# return Tip
# h = HashTag.query.join(hashtags).filter_by(tips_id=14).all()
# return HashTag by tip
# h = HashTag.query.join(hashtags).all()
# h = HashTag.query.filter(HashTag.tag=='games').first()
# h = db.session.query(HashTag).filter(HashTag.tag == 'games').first()
# get tips by hashtag id
# tips = Tip.query.join(hashtags).filter_by(hashtags_id=4).all()
# likes = t.likes.all()
# joins
# likes = db.session.query(Like, User.username).join(User, Like.user_id == User.id).all()
# likes = db.session.query(Like, User.username).filter_by(tip_id=tip_id).join(User, Like.user_id == User.id).all()
