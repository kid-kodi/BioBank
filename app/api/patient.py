from flask import jsonify, request, url_for
from app import db
from app.models import Patient
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request


@bp.route('/patient/')
def get_patients():
    patients = Patient.query.all()
    return jsonify([patient.to_json() for patient in patients])


@bp.route('/patient/<int:id>')
def get_patient(id):
    patient = Patient.query.get_or_404(id)
    return jsonify(patient.to_json())


