from flask import Blueprint

bp = Blueprint('label', __name__, template_folder='templates')

from app.label import routes
