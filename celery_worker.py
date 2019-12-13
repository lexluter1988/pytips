from app import create_app, Config, celery

app = create_app(Config or 'default')
app.app_context().push()
