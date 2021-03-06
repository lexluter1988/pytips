import logging

from flask import render_template
from flask_login import login_required

from app import db
from app.admin import bp
from app.models import Permissions, User
from app.utils.decorators import check_confirmed, permissions_required

LOG = logging.getLogger(__name__)


@bp.route('/admin', methods=['GET'])
@login_required
@check_confirmed
@permissions_required(Permissions.ADMINISTER)
def admin():
    users = db.session.query(User).all()
    return render_template('admin/admin.html', users=users)