from functools import wraps

from flask import flash, redirect, url_for
from flask_babel import gettext as _
from flask_login import current_user


def check_confirmed(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.confirmed is False:
            flash(_('Please confirm your account!'))
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)

    return decorated_function


def permissions_required(permission):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                flash(_('Insufficient permissions!'))
                return redirect(url_for('main.index'))
            return func(*args, **kwargs)
        return decorated_function
    return decorator
