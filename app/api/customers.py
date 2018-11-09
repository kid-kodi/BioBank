from flask import jsonify, request, url_for
from app import db
from app.models import Customer, Project
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request


@bp.route('/customers/')
def get_customers():
    customers = Customer.query.all()
    return jsonify([room.to_json() for room in customers])


@bp.route('/customers/<int:id>')
def get_room(id):
    room = Customer.query.get_or_404(id)
    return jsonify(room.to_json())


@bp.route('/customers/<int:id>/projects')
def get_room_projects(id):
    projects = Project.query.filter_by(customer_id=id).all()
    return jsonify([item.to_json() for item in projects])

