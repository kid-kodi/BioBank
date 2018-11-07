from flask import Blueprint

bp = Blueprint('equipment_type', __name__)

from app.equipment_type import routes
