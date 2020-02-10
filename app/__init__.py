import logging
import os
from logging.handlers import RotatingFileHandler
from logging.handlers import SMTPHandler

from celery import Celery
from flask import Flask, current_app
from flask import request
from flask_babel import Babel
from flask_babel import lazy_gettext as _l
from flask_bootstrap import Bootstrap
from flask_caching import Cache
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

from app.api.v1.resources import api
from app.logger import RequestFormatter
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = _l('Please log in to access this page.')
mail = Mail()
bootstrap = Bootstrap()
moment = Moment()
babel = Babel()
celery = Celery(
        __name__,
        backend=Config.CELERY_RESULT_BACKEND,
        broker=Config.CELERY_BROKER_URL
    )
cache = Cache(config={'CACHE_TYPE': 'simple'})


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    celery.conf.update(app.config)
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app)
    api.init_app(app)
    cache.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.tips import bp as tips_bp
    app.register_blueprint(tips_bp)

    from app.notifications import bp as notifications_bp
    app.register_blueprint(notifications_bp)

    from app.messages import bp as messages_bp
    app.register_blueprint(messages_bp)

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    from app.subscriptions import bp as subscriptions_bp
    app.register_blueprint(subscriptions_bp)

    formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s'
    )

    if not app.debug:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='Pytips Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            mail_handler.setFormatter(formatter)
            app.logger.addHandler(mail_handler)
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/pytips.log', maxBytes=10240,
                                           backupCount=10)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Pytips startup')

    return app


@babel.localeselector
def get_locale():
    if cache.get('lang'):
        return cache.get('lang')
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])
