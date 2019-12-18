from datetime import datetime

from flask import g
from flask import render_template, flash, redirect, url_for
from flask import request
from flask_babel import _
from flask_babel import get_locale
from flask_login import current_user, login_required

from app import db
from app.main import bp
from app.main.forms import EditProfileForm, MessageForm
from app.models import User, Tip, Message
from app.utils.decorators import check_confirmed


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())


@bp.route('/')
@bp.route('/index')
def index():
    return redirect(url_for('tips.get_tip'))


@bp.route('/user/<username>')
@login_required
@check_confirmed
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    tips = Tip.query.filter(Tip.user_id == current_user.id).all()
    following = list(following.id for following in current_user.followed.all())
    following_posts = Tip.query.filter(Tip.user_id.in_(following)).all()
    moderation = []
    if user.role.permissions == 255:
        moderation = Tip.query.filter_by(moderated=False).all()
    inbox = current_user.messages_received.all()
    unread = [i for i in inbox if i.status == 0]
    return render_template(
        'main/user.html', user=user, tips=tips, moderation=moderation, following_posts=following_posts, unread=unread)


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.locale = str(get_locale())


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
@check_confirmed
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('main/edit_profile.html', title='Edit Profile',
                           form=form)


@bp.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
@check_confirmed
def send_message(recipient):
    user = User.query.filter_by(username=recipient).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user, body=form.message.data)
        db.session.add(msg)
        db.session.commit()
        flash(_('Your message has been sent.'))
        return redirect(url_for('main.user', username=recipient))
    return render_template('main/send_message.html', title=_('Send Message'),
                           form=form, recipient=recipient)


@bp.route('/messages', methods=['GET'])
@login_required
@check_confirmed
def messages():
    inbox = current_user.messages_received.all()
    unread = [i for i in inbox if i.status == 0]
    sent = current_user.messages_sent.all()
    return render_template('main/messages.html', inbox=inbox, sent=sent, unread=unread)


@bp.route('/messages/<msg_id>/<status>', methods=['GET'])
@login_required
@check_confirmed
def mark_as(msg_id, status):
    message = current_user.messages_received.filter_by(id=msg_id).first()
    if message:
        message.status = status
        db.session.add(message)
        db.session.commit()
    return redirect(url_for('main.messages'))


@bp.route('/messages/<msg_id>/reply/<recipient_id>', methods=['GET', 'POST'])
@login_required
@check_confirmed
def reply(msg_id, recipient_id):
    recipient = User.query.filter_by(id=recipient_id).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=recipient, body=form.message.data, reply_id=msg_id)
        db.session.add(msg)
        db.session.commit()
        flash(_('Your reply has been sent.'))
        return redirect(url_for('main.user', username=current_user.username))
    return render_template('main/send_message.html', title=_('Send Message'),
                           form=form, recipient=recipient.username)


@bp.route('/messages/<msg_id>/delete', methods=['GET'])
@login_required
@check_confirmed
def delete(msg_id):
    message = Message.query.filter_by(id=msg_id).first()
    if message:
        db.session.delete(message)
        db.session.commit()
        flash(_('Message deleted'))
    return redirect(url_for('main.user', username=current_user.username))