from flask import Blueprint

bp = Blueprint('basket', __name__)

from app.basket import routes
