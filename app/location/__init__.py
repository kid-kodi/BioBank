from flask import Blueprint

bp = Blueprint('location', __name__, template_folder="templates")

from app.location import routes
