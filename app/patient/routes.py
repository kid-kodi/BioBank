from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.patient.forms import PatientForm
from app.models import Patient, Origin, Project, Order, SampleType, Mesure, TubeType, SampleNature, JoncType, Sample
from app.translate import translate
from app.patient import bp


@bp.route('/patient', methods=['GET', 'POST'])
@login_required
def index():
    patients = Patient.query.all()
    return render_template('patient/index.html', patients=patients)


@bp.route('/patient/add', methods=['GET', 'POST'])
@bp.route('/order/<int:order_id>/patient/add', methods=['GET', 'POST'])
@login_required
def add(order_id):
    order = None
    if order_id != 0:
        order = Order.query.get(order_id)
    form = PatientForm()
    for entry in form.samples.entries:
        entry.sample_type.choices = [(c.id, c.name) for c in SampleType.query.all()]
        entry.mesure.choices = [(c.id, c.name) for c in Mesure.query.all()]
        entry.tube_type.choices = [(c.id, c.name) for c in TubeType.query.all()]
        entry.sample_nature.choices = [(c.id, c.name) for c in SampleNature.query.all()]
        entry.jonc_type.choices = [(c.id, c.name) for c in JoncType.query.all()]

    if form.validate_on_submit():
        patient = Patient(bio_code=get_bio_code('HU'), order_id=order_id, origin_id=1, code=form.code.data,
                          sexe=form.sexe.data, birthday=form.birthday.data)
        db.session.add(patient)
        db.session.commit()

        index = 0
        for s in form.samples.entries:
            index = index + 1
            sample = Sample()
            sample.code = s.code.data
            sample.sample_nature_id = s.sample_nature.data
            sample.sample_type_id = s.sample_type.data
            sample.date = s.date.data
            sample.site = s.site.data
            sample.tube_type_id = s.tube_type.data
            sample.jonc_type_id = s.jonc_type.data
            sample.number = s.number.data
            sample.mesure_id = s.mesure.data
            sample.volume = s.volume.data
            sample.patient_id = patient.id
            sample.status = 0

            db.session.add(sample)
            db.session.commit()
            generateCode(sample, index)

        flash(_('Nouveau patient ajouté avec succèss!'))
        return redirect(url_for('order.detail', id=patient.order_id))
    return render_template('patient/form.html', form=form, order=order)


@bp.route('/patient/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    patient = Patient.query.get(id)
    form = PatientForm()
    form.order.choices = [(c.id, c.serial) for c in Order.query.all()]
    if form.validate_on_submit():
        patient.order_id = form.order.data
        patient.code = form.code.data
        patient.sexe = form.sexe.data
        patient.birthday = form.birthday.data
        db.session.commit()
        flash(_('Les informations ont été modifiées avec succèss'))
        return redirect(url_for('patient.index'))

    form.order.data = patient.order_id
    form.code.data = patient.code
    form.sexe.data = patient.sexe
    form.birthday.data = patient.birthday
    return render_template('patient/form.html', form=form)


@bp.route('/patient/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    patient = Patient.query.get(id)
    return render_template('patient/detail.html', patient=patient)


def get_bio_code(s):
    size = len(Patient.query.all()) + 1
    num = s + str(size).zfill(10)
    return num


def generateCode(s, index):
    s.code = str(s.number) + '-' + str(s.sample_nature.siggle) + str(index) + '-' + str(s.jonc_type.siggle)
    db.session.commit()
    #3SURur2 - fn - rouge
    return s
