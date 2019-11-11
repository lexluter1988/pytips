from flask import render_template

from app.tips import bp
from app.utils.tips_utils import get_random_tip


@bp.route('/tips', methods=['GET', 'POST'])
def get_tip():
    return render_template('tips/tips.html', title='Tip of a day', tip=get_random_tip())