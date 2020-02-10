import logging

from app import celery, db
from app.models import HashTag, Tip, hashtags

LOG = logging.getLogger(__name__)


@celery.task()
def cleanup_hash_tags():
    hashtags_all = db.session.query(HashTag).all()
    for hashtag in hashtags_all:
        tips = db.session.query(Tip).join(hashtags).filter_by(hashtags_id=hashtag.id).all()
        if not tips:
            db.session.delete(hashtag)
    db.session.commit()
