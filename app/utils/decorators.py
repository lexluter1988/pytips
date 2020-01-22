from functools import wraps

from flask import flash, redirect, url_for, session
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


def record_stat(type):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            print(session.get('db_stat'))
            if not session.get('db_stat'):
                session['db_stat'] = {func.__name__: 1}
            else:
                if not session.get('db_stat').get(func.__name__):
                    session['db_stat'][func.__name__] = 1
                else:
                    session['db_stat'][func.__name__] += 1
            return func(*args, **kwargs)
        return decorated_function
    return decorator
