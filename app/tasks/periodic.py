from app import celery


@celery.task()
def cleanup_hash_tags():
    print('hello world')
