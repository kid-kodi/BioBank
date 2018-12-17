from flask import Blueprint

bp = Blueprint('disease', __name__, template_folder='templates')

from app.disease import routes
