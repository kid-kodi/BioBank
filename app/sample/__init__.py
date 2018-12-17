from flask import Blueprint

bp = Blueprint('sample', __name__, template_folder="templates")

from app.sample import routes
