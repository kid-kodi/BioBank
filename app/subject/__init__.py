from flask import Blueprint

bp = Blueprint('subject', __name__)

from app.subject import routes
