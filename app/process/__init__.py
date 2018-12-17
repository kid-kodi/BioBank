from flask import Blueprint

bp = Blueprint('process', __name__, template_folder="templates")

from app.process import routes
