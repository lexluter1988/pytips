from flask import Blueprint

bp = Blueprint('tips', __name__)

from app.tips import routes