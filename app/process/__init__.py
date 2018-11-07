from flask import Blueprint

bp = Blueprint('process', __name__)

from app.process import routes
