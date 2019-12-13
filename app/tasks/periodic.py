from app import celery


@celery.task
def send_async_hello():
    print('hello world')
