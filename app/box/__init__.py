from flask import Blueprint

bp = Blueprint('box', __name__)

from app.box import routes
