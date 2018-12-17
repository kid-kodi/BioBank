from flask import Blueprint

bp = Blueprint('project', __name__, template_folder='templates')

from app.project import routes
