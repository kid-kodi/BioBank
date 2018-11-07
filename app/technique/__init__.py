from flask import Blueprint

bp = Blueprint('technique', __name__)

from app.technique import routes
