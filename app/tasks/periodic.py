import logging

from app import celery, db
from app.models import HashTag, Tip, hashtags
from app.utils import query

LOG = logging.getLogger(__name__)


@celery.task()
def cleanup_hash_tags():
    hashtags_all = query.get_hashtags()
    for hashtag in hashtags_all:
        tips = query.get_tips_by_hashtag(hashtag)
        if not tips:
            db.session.delete(hashtag)
    db.session.commit()
