from flask import Blueprint

bp = Blueprint('aliquot', __name__, template_folder='templates')

from app.aliquot import routes
