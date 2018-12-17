from flask import Blueprint

bp = Blueprint('support', __name__, template_folder='templates')

from app.support import routes
