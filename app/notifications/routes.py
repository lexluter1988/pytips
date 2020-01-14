import logging

from flask import jsonify
from flask_login import current_user
from app.notifications import bp

LOG = logging.getLogger(__name__)


@bp.route('/notifications', methods=['GET'])
def notifications():
    if current_user.is_anonymous:
        return jsonify([])
    notifications = current_user.notifications.all()
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications])