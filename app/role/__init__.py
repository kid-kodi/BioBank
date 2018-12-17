from flask import Blueprint

bp = Blueprint('role', __name__, template_folder='templates')

from app.role import routes
