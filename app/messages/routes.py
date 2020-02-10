import logging

from flask import flash, redirect, render_template, url_for
from flask_babel import gettext as _
from flask_login import login_required, current_user

from app import db
from app.messages import bp
from app.messages.forms import MessageForm, NewMessageForm
from app.models import User, Message
from app.utils.decorators import check_confirmed
from app.utils.formatter import format_reply

LOG = logging.getLogger(__name__)


def _sent_message(author, recipient, message):
    msg = Message(author=author, recipient=recipient, body=message)
    db.session.add(msg)
    recipient.add_notification('new_message', current_user.username)
    db.session.commit()
    flash(_('Your message has been sent.'))


@bp.route('/message/', methods=['GET', 'POST'])
@login_required
@check_confirmed
def new_message():
    form = NewMessageForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by(username=form.user.data).first_or_404()
        _sent_message(current_user, user, form.message.data)
        return redirect(url_for('main.user', username=current_user.username))
    return render_template('messages/new_message.html', title=_('Send Message'),
                           form=form, recipient=current_user)


@bp.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
@check_confirmed
def send_message(recipient):
    user = db.session.query(User).filter_by(username=recipient).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        _sent_message(current_user, user, form.message.data)
        return redirect(url_for('main.user', username=recipient))
    return render_template('messages/send_message.html', title=_('Send Message'),
                           form=form, recipient=recipient)


@bp.route('/messages', methods=['GET'])
@login_required
@check_confirmed
def messages():
    current_user.notifications.delete()
    db.session.commit()
    inbox = current_user.messages_received.all()
    unread = [i for i in inbox if i.status == 0]
    sent = current_user.messages_sent.all()
    return render_template('messages/messages.html', inbox=inbox, sent=sent, unread=unread)


@bp.route('/messages/<msg_id>/<status>', methods=['GET'])
@login_required
@check_confirmed
def mark_as(msg_id, status):
    message = current_user.messages_received.filter_by(id=msg_id).first()
    if message:
        message.status = status
        db.session.add(message)
        db.session.commit()
    return redirect(url_for('messages.messages'))


@bp.route('/messages/<msg_id>/reply/<recipient_id>', methods=['GET', 'POST'])
@login_required
@check_confirmed
def reply(msg_id, recipient_id):
    recipient = db.session.query(User).filter_by(id=recipient_id).first_or_404()
    message = db.session.query(Message).filter_by(id=msg_id).first()
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=recipient, body=form.message.data, reply_id=msg_id)
        db.session.add(msg)
        recipient.add_notification('new_message', current_user.username)
        db.session.commit()
        flash(_('Your reply has been sent.'))
        return redirect(url_for('main.user', username=current_user.username))
    return render_template('messages/send_message.html', title=_('Send Message'),
                           form=form, recipient=recipient.username,
                           message=format_reply(recipient.username, message.body))


@bp.route('/messages/<msg_id>/delete', methods=['GET'])
@login_required
@check_confirmed
def delete(msg_id):
    message = db.session.query(Message).filter_by(id=msg_id).first()
    if message:
        db.session.delete(message)
        db.session.commit()
        flash(_('Message deleted'))
    return redirect(url_for('main.user', username=current_user.username))
