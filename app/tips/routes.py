import random
import re

from flask import render_template, flash, redirect, url_for, request, session, current_app
from flask_babel import gettext as _
from flask_login import current_user, login_required

from app import db
from app.models import Tip, HashTag, hashtags, User, Like, Permissions
from app.tips import bp
from app.tips.forms import TipForm
from app.utils.decorators import check_confirmed, permissions_required


def _append_hashtags(tip, form):
    hashtags = re.findall(r'\#\w+', form.hashtags.data)
    for hashtag in hashtags:
        tag = HashTag.query.filter(HashTag.tag == hashtag).first()
        if not tag:
            tag = HashTag(tag=hashtag)
            db.session.add(tag)
        tip.hashtags.append(tag)


@bp.route('/tips', methods=['GET'])
def get_tip():
    current_app.logger.info('dbg,  getting post')
    tips = Tip.query.all()
    if tips:
        session['tips'] = random.shuffle(tips)
        rand = random.randint(0, len(tips) - 1)
        tip_of_the_day = tips[rand]
        likes = tip_of_the_day.likes.all()
    else:
        return render_template('tips/tips.html', title='Tip of a day')
    return render_template('tips/tips.html', title='Tip of a day', tip=tip_of_the_day, likes=likes)


@bp.route('/tips/<tip_id>', methods=['GET'])
def get_tip_by_id(tip_id):
    tip = db.session.query(Tip).filter(Tip.id == tip_id).first()
    if tip:
        likes = tip.likes.all()
    else:
        return render_template('tips/tips.html', title='Tip of a day')
    return render_template('tips/tips.html', title='Tip of a day', tip=tip, likes=likes)


@bp.route('/tips/new', methods=['GET', 'POST'])
@login_required
@check_confirmed
def create_tip():
    form = TipForm()
    if form.validate_on_submit():
        tip = Tip(body=form.tip.data, author=current_user)
        _append_hashtags(tip, form)
        db.session.add(tip)
        db.session.commit()
        flash(_('Your tip is now live!'))
        return redirect(url_for('tips.get_tip'))
    return render_template('tips/new_tips.html', title='Create new tip of a day', form=form)


@bp.route('/tips/edit/<tip_id>', methods=['GET', 'POST'])
@login_required
@check_confirmed
def edit_tip(tip_id):
    form = TipForm()
    tip = db.session.query(Tip).filter(Tip.id == tip_id).first()
    if current_user.id != tip.user_id:
        if current_user.email not in current_app.config['ADMINS']:
            flash(_('You cannot change others tips, unless you are admin!'))
            return redirect(url_for('tips.get_tip'))
    hashtags_old = [hashtag.tag for hashtag in tip.hashtags]
    if form.validate_on_submit():
        tip.body = form.tip.data
        hashtags_new = re.findall(r'\#\w+', form.hashtags.data)
        _append_hashtags(tip, form)
        hashtags_diff = list(set(hashtags_old) - set(hashtags_new))
        for hashtag in hashtags_diff:
            tag = HashTag.query.filter(HashTag.tag == hashtag).first()
            tip.hashtags.remove(tag)
        # clean up unused hashtags
        # TODO: implement via periodic task
        hashtags_all = HashTag.query.all()
        for hashtag in hashtags_all:
            tips = Tip.query.join(hashtags).filter_by(hashtags_id=hashtag.id).all()
            if not tips:
                db.session.delete(hashtag)
        db.session.commit()
        flash(_('Your tip has been changed!'))
        return redirect(url_for('tips.get_tip'))
    elif request.method == 'GET':
        form.tip.data = tip.body
        form.hashtags.data = ' '.join(hashtags_old)
    return render_template('tips/new_tips.html', title='Edit tip', form=form)


@bp.route('/tips/get_by_hashtag/<hashtag_id>', methods=['GET'])
def get_tips_by_hashtag(hashtag_id):
    hashtag = HashTag.query.filter(HashTag.id == hashtag_id).first()
    tips = Tip.query.join(hashtags).filter_by(hashtags_id=hashtag_id).all()
    return render_template('tips/tips_by_hashtag.html', title='Tips by hashtag', tips=tips, hashtag=hashtag)


@bp.route('/tips/moderate/<tip_id>', methods=['GET'])
@login_required
@check_confirmed
@permissions_required(Permissions.ADMINISTER)
def moderate_tip(tip_id):
    tip = Tip.query.filter_by(id=tip_id).first()
    tip.moderated = True
    db.session.add(tip)
    db.session.commit()
    flash(_('Tip approved'))
    return redirect(url_for('main.user', username=current_user.username))


@bp.route('/follow/<username>', methods=['GET'])
@login_required
@check_confirmed
def follow(username):
    user = User.query.filter_by(username=username).first()
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
    user = User.query.filter_by(username=username).first()
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


@bp.route('/like/<tip_id>', methods=['GET'])
@login_required
@check_confirmed
def like(tip_id):
    existing = Like.query.filter_by(user_id=current_user.id).filter_by(tip_id=tip_id).first()
    if existing:
        flash(_('You already liked that post! Removing like'))
        db.session.delete(existing)
        db.session.commit()
        return redirect(url_for('tips.get_tip'))
    like = Like(user_id=current_user.id, tip_id=tip_id)
    db.session.add(like)
    db.session.commit()
    flash(_('You liked that post!'))
    return redirect(url_for('tips.get_tip'))


@bp.route('/like/who_liked/<tip_id>', methods=['GET'])
@login_required
@check_confirmed
def who_liked(tip_id):
    likes = db.session.query(Like, User.username).filter_by(tip_id=tip_id).join(User, Like.user_id == User.id).all()
    return render_template('tips/tips_who_liked.html', title='Likes', likes=likes)
