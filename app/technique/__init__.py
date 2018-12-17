from flask import Blueprint

bp = Blueprint('technique', __name__, template_folder='templates')

from app.technique import routes
