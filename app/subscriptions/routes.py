from flask import flash, redirect, url_for
from flask_babel import gettext as _
from flask_login import current_user

from app.subscriptions import bp


@bp.route('/subscribe/<type>')
def subscribe(type):
    flash(_('You subscribed to {}'.format(type)))
    return redirect(url_for('main.user', username=current_user.username))


@bp.route('/unsubscribe/<type>')
def unsubscribe(type):
    flash(_('You unsubscribed to {}'.format(type)))
    return redirect(url_for('main.user', username=current_user.username))