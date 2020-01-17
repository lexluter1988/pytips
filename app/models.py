import json
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
    return db.session.query(User).get(int(id))


hashtags = db.Table('hashtags_tips',
                    db.Column('hashtags_id', db.Integer, db.ForeignKey('hashtags.id'), primary_key=True),
                    db.Column('tips_id', db.Integer, db.ForeignKey('tips.id'), primary_key=True))

followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('users.id')))


class Permissions:
    READ = 0x01
    COMMENT = 0x02
    WRITE = 0x04
    MODERATE = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role {}>'.format(self.name)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    confirmed = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    tips = db.relationship('Tip', backref='author', lazy='dynamic')
    followed = db.relationship('User', secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    notifications = db.relationship('Notification', backref='user',
                                    lazy='dynamic')

    messages_sent = db.relationship('Message',
                                    foreign_keys='Message.sender_id',
                                    backref='author', lazy='dynamic')
    messages_received = db.relationship('Message',
                                        foreign_keys='Message.recipient_id',
                                        backref='recipient', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email in current_app.config['ADMINS']:
                self.role = db.session.query(Role).filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = db.session.query(Role).filter_by(name='User').first()

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions == permissions)

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

    def add_notification(self, name, data):
        self.notifications.filter_by(name=name).delete()
        notification = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(notification)
        return notification

    @staticmethod
    def insert_roles():
        roles = {
            'User': Permissions.READ | Permissions.WRITE | Permissions.COMMENT,
            'Moderator': Permissions.READ | Permissions.WRITE | Permissions.COMMENT | Permissions.MODERATE,
            'Administrator': 0xff
        }
        for r in roles:
            role = db.session.query(Role).filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r]
            db.session.add(role)
            db.session.commit()

    @staticmethod
    def verify_token(token, token_type='reset_password'):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])[token_type]
        except Exception as e:
            current_app.logger.error('Error {}'.format(e))
            return
        return db.session.query(User).get(id)


class Tip(db.Model):
    __tablename__ = 'tips'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    moderated = db.Column(db.Boolean, default=False)
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


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body = db.Column(db.String(140))
    status = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    reply_id = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<Message {}>'.format(self.body)


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.Float, index=True, default=time)
    payload_json = db.Column(db.Text)

    def get_data(self):
        return json.loads(str(self.payload_json))


class Stat(db.Model):
    __tablename__ = 'stats'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Float, index=True, default=time)
    type = db.Column(db.Text)


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
