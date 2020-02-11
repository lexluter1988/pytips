from flask_login import current_user

from app import db
from app.models import Tip, Like, User, HashTag, hashtags
from typing import List


def tips_all():
    return db.session.query(Tip).filter(Tip.moderated).order_by(Tip.timestamp.desc()).all()


def search_tip(pattern: str) -> List[Tip]:
    return db.session.query(Tip).filter(Tip.body.like(pattern)).order_by(Tip.timestamp.desc()).filter(Tip.moderated).all()


def tip_by_id(tip_id: int) -> Tip:
    return db.session.query(Tip).filter_by(id=tip_id).first()


def who_liked(tip: Tip) -> List[Like]:
    return db.session.query(Like, User.username).filter_by(tip_id=tip.id).join(User, Like.user_id == User.id).all()


def likes(tip_id: int) -> List[tuple]:
    return db.session.query(Like, User.username).filter_by(tip_id=tip_id).join(User, Like.user_id == User.id).all()


def existing_likes(tip_id: int) -> List[Like]:
    return db.session.query(Like).filter_by(user_id=current_user.id).filter_by(tip_id=tip_id).first()


def get_tips_by_hashtag(hashtag: HashTag) -> List[Tip]:
    return db.session.query(Tip).join(hashtags).filter_by(hashtags_id=hashtag.id).all()


def get_tips_by_hashtag_id(hashtag_id: int) -> List[Tip]:
    return db.session.query(Tip).join(hashtags).filter_by(hashtags_id=hashtag_id).all()


def get_hashtags() -> List[HashTag]:
    return db.session.query(HashTag).all()


def get_hashtag(hashtag: str) -> HashTag:
    return db.session.query(HashTag).filter(HashTag.tag == hashtag).first()


def get_hashtag_by_id(hashtag_id: int) -> HashTag:
    return db.session.query(HashTag).filter(HashTag.id == hashtag_id).first()
