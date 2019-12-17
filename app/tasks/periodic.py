from app import celery, db
from app.models import HashTag, Tip, hashtags


@celery.task()
def cleanup_hash_tags():
    hashtags_all = HashTag.query.all()
    for hashtag in hashtags_all:
        tips = Tip.query.join(hashtags).filter_by(hashtags_id=hashtag.id).all()
        if not tips:
            db.session.delete(hashtag)
    db.session.commit()
