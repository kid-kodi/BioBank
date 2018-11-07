from flask import Blueprint

bp = Blueprint('program', __name__)

from app.program import routes
