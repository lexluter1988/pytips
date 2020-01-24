import logging
from datetime import datetime

from flask import g, session
from flask import render_template, flash, redirect, url_for
from flask import request
from flask_babel import _
from flask_babel import get_locale
from flask_login import current_user, login_required

from app import db
from app.main import bp
from app.main.forms import EditProfileForm
from app.models import User, Tip
from app.utils.decorators import check_confirmed, record_stat

LOG = logging.getLogger(__name__)


@bp.before_app_request
def before_request():
    if not session.get('visits'):
        session['visits'] = {str(request.remote_addr): True}
    else:
        if not session.get('visits').get(str(request.remote_addr)):
            session['visits'][str(request.remote_addr)] = True

    # TODO: periodic task to save that to db.
    #LOG.debug('visits', len(session.get('visits')))

    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())


@bp.route('/')
@bp.route('/index')
def index():
    return redirect(url_for('tips.get_tip'))


@bp.route('/language/<lang>')
def language(lang):
    session['lang'] = lang
    flash(_('Language has been changed.'))
    return redirect(url_for('tips.get_tip'))


@bp.route('/user/<username>')
@login_required
@check_confirmed
@record_stat('test')
def user(username):
    user = db.session.query(User).filter_by(username=username).first_or_404()
    tips = db.session.query(Tip).filter(Tip.user_id == current_user.id).all()
    following = list(following.id for following in current_user.followed.all())
    following_posts = db.session.query(Tip).filter(Tip.user_id.in_(following)).all()
    moderation = []
    if user.role.permissions == 255:
        moderation = db.session.query(Tip).filter_by(moderated=False).all()
    inbox = current_user.messages_received.all()
    unread = [i for i in inbox if i.status == 0]
    return render_template(
        'main/user.html', user=user, tips=tips, moderation=moderation, following_posts=following_posts, unread=unread)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
@check_confirmed
@record_stat('test')
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = current_user.username
        current_user.about_me = form.about_me.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.about_me.data = current_user.about_me
    return render_template('main/edit_profile.html', title='Edit Profile',
                           form=form)


@bp.route('/follow/<username>', methods=['GET'])
@login_required
@check_confirmed
def follow(username):
    user = db.session.query(User).filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('tips.get_tip'))
    if user == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('tips.get_tip'))
    current_user.follow(user)
    db.session.commit()
    flash(_('You are following %(username)s!', username=username))
    return redirect(url_for('tips.get_tip'))


@bp.route('/unfollow/<username>', methods=['GET'])
@login_required
@check_confirmed
def unfollow(username):
    user = db.session.query(User).filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('tips.get_tip'))
    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('tips.get_tip'))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s!', username=username))
    return redirect(url_for('tips.get_tip'))
