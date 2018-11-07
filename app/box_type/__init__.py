from flask import Blueprint

bp = Blueprint('box_type', __name__)

from app.box_type import routes
