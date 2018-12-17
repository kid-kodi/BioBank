from flask import Blueprint

bp = Blueprint('program', __name__, template_folder='templates')

from app.program import routes
