from flask import Blueprint

bp = Blueprint('sample_type', __name__, template_folder='templates')

from app.sample_type import routes
