import random
import re

from flask import render_template, flash, redirect, url_for, request
from flask_babel import gettext as _
from flask_login import current_user, login_required

from app import db
from app.models import Tip, HashTag, hashtags
from app.tips import bp
from app.tips.forms import TipForm


@bp.route('/tips', methods=['GET'])
def get_tip():
    tips = Tip.query.all()
    rand = random.randint(0, len(tips) - 1)
    return render_template('tips/tips.html', title='Tip of a day', tip=tips[rand])


@bp.route('/tips/new', methods=['GET', 'POST'])
@login_required
def create_tip():
    form = TipForm()
    if form.validate_on_submit():
        tip = Tip(body=form.tip.data, author=current_user)
        hashtags = re.findall(r'\#\w+', form.hashtags.data)
        for hashtag in hashtags:
            tag = HashTag.query.filter(HashTag.tag == hashtag).first()
            if not tag:
                tag = HashTag(tag=hashtag)
                db.session.add(tag)
            tip.hashtags.append(tag)

        db.session.add(tip)
        db.session.commit()
        flash(_('Your tip is now live!'))
        return redirect(url_for('tips.get_tip'))
    return render_template('tips/new_tips.html', title='Create new tip of a day', form=form)


@bp.route('/tips/edit/<tip_id>', methods=['GET', 'POST'])
@login_required
def edit_tip(tip_id):
    form = TipForm()
    tip = db.session.query(Tip).filter(Tip.id == tip_id).first()
    hashtags_old = [hashtag.tag for hashtag in tip.hashtags]
    if form.validate_on_submit():
        tip.body = form.tip.data
        hashtags_new = re.findall(r'\#\w+', form.hashtags.data)
        for hashtag in hashtags_new:
            tag = HashTag.query.filter(HashTag.tag == hashtag).first()
            if not tag:
                tag = HashTag(tag=hashtag)
                db.session.add(tag)
            tip.hashtags.append(tag)
        # remove tags that were not in the new version of tip
        hashtags_diff = list(set(hashtags_old) - set(hashtags_new))
        for hashtag in hashtags_diff:
            tag = HashTag.query.filter(HashTag.tag == hashtag).first()
            tip.hashtags.remove(tag)
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
