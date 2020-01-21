from flask import Blueprint

bp = Blueprint('subscriptions', __name__)

from app.subscriptions import routes