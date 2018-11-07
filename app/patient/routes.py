from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.patient.forms import PatientForm
from app.models import Patient, Origin
from app.translate import translate
from app.patient import bp


@bp.route('/patient', methods=['GET', 'POST'])
@login_required
def index():
    patients = Patient.query.all()
    return render_template('patient/index.html', patients=patients)


@bp.route('/patient/add', methods=['GET', 'POST'])
@login_required
def add():
    form = PatientForm()
    form.origin.choices = [(c.id, c.name) for c in Origin.query.all()]
    if form.validate_on_submit():
        patient = Patient(origin_id=form.origin.data, code=form.code.data,
                          sexe=form.sexe.data, birthday=form.birthday.data)
        db.session.add(patient)
        db.session.commit()
        flash(_('Nouveau patient ajouté avec succèss!'))
        return redirect(url_for('patient.detail', id=patient.id))
    return render_template('patient/form.html', form=form)


@bp.route('/patient/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    patient = Patient.query.get(id)
    form = PatientForm()
    form.origin.choices = [(c.id, c.name) for c in Origin.query.all()]
    if form.validate_on_submit():
        patient.origin_id = form.origin.data
        patient.code = form.code.data
        patient.sexe = form.sexe.data
        patient.birthday = form.birthday.data
        db.session.commit()
        flash(_('Les informations ont été modifiées avec succèss'))
        return redirect(url_for('patient.index'))

    form.origin.data   = patient.origin_id
    form.code.data     = patient.code
    form.sexe.data     = patient.sexe
    form.birthday.data = patient.birthday
    return render_template('patient/form.html', form=form)


@bp.route('/patient/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    patient = Patient.query.get(id)
    return render_template('patient/detail.html', patient=patient)
