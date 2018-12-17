from flask import Blueprint

bp = Blueprint('study', __name__, template_folder='templates')

from app.study import routes
