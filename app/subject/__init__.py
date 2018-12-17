from flask import Blueprint

bp = Blueprint('subject', __name__, template_folder='templates')

from app.subject import routes
