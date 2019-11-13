import random

from flask import render_template, flash, redirect, url_for
from flask_babel import gettext as _
from flask_login import current_user, login_required

from app import db
from app.models import Tip
from app.tips import bp
from app.tips.forms import TipForm
from app.utils.tips_utils import get_random_tip


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
        tip = Tip(body=form.post.data, author=current_user)
        db.session.add(tip)
        db.session.commit()
        flash(_('Your tip is now live!'))
        return redirect(url_for('tips.get_tip'))
    return render_template('tips/new_tips.html', title='Create new tip of a day', form=form)

