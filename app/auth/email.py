import logging
from threading import Thread

from flask import current_app
from flask import render_template
from flask_mail import Message

from app import mail

LOG = logging.getLogger(__name__)


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()


def send_password_reset_email(user):
    token = user.get_token(token_type='reset_password')
    send_email('Reset Your Password',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('auth/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('auth/reset_password.html',
                                         user=user, token=token))


def send_registration_confirm_email(user):
    token = user.get_token(token_type='registration_confirm')
    send_email('Confirm your account',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('auth/registration_confirm.txt',
                                         user=user, token=token),
               html_body=render_template('auth/registration_confirm.html',
                                         user=user, token=token))
