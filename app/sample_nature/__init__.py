from flask import Blueprint

bp = Blueprint('sample_nature', __name__, template_folder='templates')

from app.sample_nature import routes
