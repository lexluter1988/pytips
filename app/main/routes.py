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
from app.utils.decorators import check_confirmed

LOG = logging.getLogger(__name__)


@bp.before_app_request
def before_request():
    # if session.get(str(request.remote_addr), None):
    #     print('flag already set {}'.format(session.get(str(request.remote_addr))))
    # else:
    #     print('setting visit flag for that ip')
    #     session[str(request.remote_addr)] = True
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