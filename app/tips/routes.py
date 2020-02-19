import logging
import re
from io import BytesIO
from reportlab.pdfgen import canvas
from flask import render_template, flash, redirect, url_for, request, current_app, jsonify, Response
from flask_babel import gettext as _
from flask_login import current_user, login_required

from app import db
from app.models import Tip, HashTag, Like, Permissions
from app.tips import bp
from app.tips.forms import TipForm
from app.utils.decorators import check_confirmed, permissions_required
from app.utils import query

LOG = logging.getLogger(__name__)


def _append_hashtags(tip, form):
    hashtags = re.findall(r'\#\w+', form.hashtags.data)
    for hashtag in hashtags:
        tag = query.get_hashtag(hashtag)
        if not tag:
            tag = HashTag(tag=hashtag)
            db.session.add(tag)
        tip.hashtags.append(tag)


@bp.route('/tips', methods=['GET'])
def get_tip():
    tips = query.tips_all()
    for tip in tips:
        tip.who_liked = query.who_liked(tip)
    return render_template('tips/tips.html', title='Tip of a day', tips=tips)


@bp.route('/tips/<tip_id>', methods=['GET'])
def get_tip_by_id(tip_id):
    tip = query.tip_by_id(tip_id)
    tip.who_liked = query.who_liked(tip)
    return render_template('tips/tips.html', title='Tip of a day', tips=[tip])


@bp.route('/tips/get_by_user_id/<user_id>', methods=['GET'])
def get_tip_by_user_id(user_id):
    tips = db.session.query(Tip).filter(Tip.user_id == user_id).order_by(Tip.timestamp.desc()).all()
    for tip in tips:
        tip.who_liked = query.who_liked(tip)
    return render_template('tips/tips.html', title='Tip of a day', tips=tips)


@bp.route('/tips/get_by_hashtag/<hashtag_id>', methods=['GET'])
def get_tips_by_hashtag(hashtag_id):
    hashtag = query.get_hashtag_by_id(hashtag_id)
    tips = query.get_tips_by_hashtag_id(hashtag_id)
    return render_template('tips/tips.html', title='Tips by hashtag', tips=tips, hashtag=hashtag)


@bp.route('/tips/hashtags', methods=['GET'])
def get_all_hashtags():
    hashtags = query.get_hashtags()
    return jsonify([hashtag.tag for hashtag in hashtags])


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
    tip = query.tip_by_id(tip_id)
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
            tag = query.get_hashtag(hashtag)
            tip.hashtags.remove(tag)
        db.session.commit()
        flash(_('Your tip has been changed!'))
        return redirect(url_for('tips.get_tip'))
    elif request.method == 'GET':
        form.tip.data = tip.body
        form.hashtags.data = ' '.join(hashtags_old)
    return render_template('tips/edit_tip.html', title='Edit tip', form=form)


@bp.route('/tips/moderate/<tip_id>', methods=['GET'])
@login_required
@check_confirmed
@permissions_required(Permissions.ADMINISTER)
def moderate_tip(tip_id):
    tip = query.tip_by_id(tip_id)
    tip.moderated = True
    db.session.add(tip)
    db.session.commit()
    flash(_('Tip approved'))
    return redirect(url_for('main.user', username=current_user.username))


@bp.route('/tips/delete/<tip_id>', methods=['GET'])
@login_required
@check_confirmed
def delete_tip(tip_id):
    tip = query.tip_by_id(tip_id)
    if current_user.id != tip.user_id:
        if current_user.email not in current_app.config['ADMINS']:
            flash(_('You cannot delete other users tips unless you admin!'))
            return redirect(url_for('main.user', username=current_user.username))
    db.session.delete(tip)
    db.session.commit()
    flash(_('Tip deleted!'))
    return redirect(url_for('main.user', username=current_user.username))


@bp.route('/like/<tip_id>', methods=['GET'])
@login_required
@check_confirmed
def like(tip_id):
    existing = query.existing_likes(tip_id)
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
    likes = query.likes(tip_id)
    return render_template('tips/tips_who_liked.html', title='Likes', likes=likes)


@bp.route('/tips/search')
def search():
    if request.method == 'GET':
        pattern = '%' + request.args.get("pattern", "") + '%'
        if pattern:
            result = query.search_tip(pattern)
            return render_template('tips/search_results.html', title='Search Results', tips=result)
    return redirect(url_for('tips.get_tip'))


@bp.route('/tips/download/<tip_id>')
def download(tip_id):
    tip = query.tip_by_id(tip_id)
    response = Response(content_type='application/pdf')
    response.headers['Content-Disposition'] = 'inline; filename="mypdf.pdf"'

    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    # Start writing the PDF here
    p.drawString(100, 100, tip.body)
    # End writing

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()

    return redirect(url_for('static', filename='masteringopenstack.pdf'))
