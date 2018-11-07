from flask import Blueprint

bp = Blueprint('study', __name__)

from app.study import routes
