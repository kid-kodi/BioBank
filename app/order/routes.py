import os
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, send_from_directory
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db, documents
from app.order.forms import OrderForm, ImportForm
from app.models import Order, Customer, Project, Patient, Sample, Origin, SampleType, Mesure, Support, SampleNature, \
    JoncType, Temperature, Document, Basket
from app.translate import translate
from app.order import bp
import pandas as pd

basedir = ''


@bp.route('/order', methods=['GET', 'POST'])
@login_required
def index():
    orders = Order.query.all()
    return render_template('order/index.html', orders=orders)


@bp.route('/order/download_file/<filename>')
def download_file(filename):
   return send_from_directory(current_app.config['UPLOADS_DEFAULT_DEST'], filename, as_attachment=True)


@bp.route('/order/add', methods=['GET', 'POST'])
@bp.route('/project/<int:project_id>/order/add', methods=['GET', 'POST'])
@login_required
def add(project_id=0):
    project = None
    form = OrderForm()
    if project_id != 0:
        project = Project.query.get(project_id)
        form.customer.data = project.customer_id
        form.project.data = project.id

    form.customer.choices = [(c.id, c.display_as) for c in Customer.query.all()]
    form.project.choices = [(c.id, c.title) for c in Project.query.all()]
    form.temperature.choices = [(c.id, c.name) for c in Temperature.query.all()]

    if form.validate_on_submit():
        order = Order()

        if 'file' in request.files:
            file = request.files['file']
            order.file_name = documents.save(file)
            order.file_url = documents.url(order.file_name)

        order.serial = get_order_code()
        order.project_id = form.project.data
        order.first_name = form.first_name.data
        order.last_name = form.last_name.data
        order.telephone = form.telephone.data
        order.receive_date = form.receive_date.data
        order.send_date = form.send_date.data
        order.temperature_id = form.temperature.data
        order.nbr_pack = form.nbr_pack.data
        order.timestamp = datetime.utcnow()
        order.user_id = current_user.id
        order.status = 0
        db.session.add(order)
        db.session.commit()

        flash(_('Informations du dépôt enregistrées!'))
        return redirect(url_for('order.detail', id=order.id))

    return render_template('order/form.html', form=form, project=project)


@bp.route('/order/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    order = Order.query.get(id)
    return render_template('order/detail.html', order=order)


@bp.route('/order/validate/<int:id>', methods=['GET', 'POST'])
@login_required
def validate(id):
    order = Order.query.get(id)
    data_xls = pd.read_excel(order.file_url)
    for index, row in data_xls.iterrows():
        # one patient have samples that have results
        # check patient number first if exist in db per row
        patient = Patient()
        patient_count = Patient.query.filter_by(code=row[0]).count()
        if patient_count > 0:
            sample_count = Sample.query.filter_by(code=row[7]).count()
            if sample_count > 0:
                # add new resltuts
                print(row[0] + ' ' + str(index))
            else:
                sample = Sample()
                sample.origin_id = 1
                sample.bio_code = patient.bio_code
                sample.volume = row[16]
                sample_nature = SampleNature.query.filter_by(name=row[8]).first()
                sample.sample_nature_id = sample_nature.id

                print(row[14])
                sample_type = SampleType.query.filter_by(name=row[9]).first()
                sample.sample_type_id = sample_type.id

                support = Support.query.filter_by(name=row[13]).first()
                sample.support_id = support.id

                jonc_type = JoncType.query.filter_by(name=row[14]).first()
                if jonc_type is not None:
                    sample.jonc_type_id = jonc_type.id

                mesure = Mesure.query.filter_by(name=row[17]).first()
                sample.mesure_id = mesure.id

                sample.code = row[7]
                sample.date = str(row[10])
                sample.technique = row[11]
                sample.site = row[12]
                sample.status = 0

                patient.samples.append(sample)
                order.patients.append(patient)
                db.session.commit()
                generateCode(sample, index + 1)

        else:
            # add new patient and samples and result of sample
            patient.code = row[0]
            patient.origin_id = 1
            patient.bio_code = get_bio_code('HU')
            patient.age = row[1]
            patient.sexe = row[2]
            patient.birthday = str(row[3])
            patient.city = row[4]
            patient.job = row[5]
            patient.clinical_data = row[6]
            # samples implementation
            for r in range(int(row[15])):
                sample = Sample()
                sample.origin_id = 1
                sample.bio_code = patient.bio_code
                sample.volume = row[16]
                sample_nature = SampleNature.query.filter_by(name=row[8]).first()
                sample.sample_nature = sample_nature

                sample_type = SampleType.query.filter_by(name=row[9]).first()
                sample.sample_type = sample_type

                support = Support.query.filter_by(name=row[13]).first()
                sample.support = support

                jonc_type = JoncType.query.filter_by(name=row[14]).first()
                sample.jonc_type = jonc_type

                mesure = Mesure.query.filter_by(name=row[17]).first()
                sample.mesure_id = mesure.id

                sample.code = row[7]
                sample.date = str(row[10])
                sample.technique = row[11]
                sample.site = row[12]
                sample.status = 0
                sample.number = int(row[15])

                patient.samples.append(sample)
                generateCode(sample, r + 1)

                print(str(sample.bio_code))
            order.patients.append(patient)
            db.session.commit()
        order.status = 1
        db.session.commit()
        # and check sample id if already in db
    flash(_('Traitement effectué avec succes!'))
    return redirect(url_for('order.detail', id=order.id))


@bp.route('/order/import/<int:id>', methods=['GET', 'POST'])
@login_required
def do_import(id):
    order = Order.query.get(id)
    if request.method == 'POST':
        file = request.files['file']
        filename = documents.save(file)

        data_xls = pd.read_excel(file)

        for index, row in data_xls.iterrows():
            # one patient have samples that have results
            # check patient number first if exist in db per row
            patient = Patient()
            patient_count = Patient.query.filter_by(code=row[0]).count()
            if patient_count > 0:
                sample_count = Sample.query.filter_by(code=row[7]).count()
                if sample_count > 0:
                    # add new resltuts
                    print(row[0] + ' ' + str(index))
                else:
                    sample = Sample()
                    sample.bio_code = patient.bio_code
                    sample.volume = row[16]
                    sample_nature = SampleNature.query.filter_by(name=row[8]).first()
                    sample.sample_nature_id = sample_nature.id

                    sample_type = SampleType.query.filter_by(name=row[9]).first()
                    sample.sample_type_id = sample_type.id

                    support = Support.query.filter_by(name=row[13]).first()
                    sample.support_id = support.id

                    jonc_type = JoncType.query.filter_by(name=row[14]).first()
                    sample.jonc_type_id = jonc_type.id

                    mesure = Mesure.query.filter_by(name=row[17]).first()
                    sample.mesure_id = mesure.id

                    sample.code = row[7]
                    sample.date = str(row[10])
                    sample.technique = row[11]
                    sample.site = row[12]
                    sample.status = 0

                    patient.samples.append(sample)
                    order.patients.append(patient)
                    db.session.commit()
                    generateCode(sample, r + 1)

            else:
                # add new patient and samples and result of sample
                print(row[4] + ' ' + str(index))
                patient.code = row[0]
                patient.origin_id = 1
                patient.bio_code = get_bio_code('HU')
                patient.age = row[1]
                patient.sexe = row[2]
                patient.birthday = str(row[3])
                patient.city = row[4]
                patient.job = row[5]
                patient.clinical_data = row[6]
                # samples implementation
                for r in range(int(row[15])):
                    sample = Sample()
                    sample.bio_code = patient.bio_code
                    sample.volume = row[16]
                    sample_nature = SampleNature.query.filter_by(name=row[8]).first()
                    sample.sample_nature_id = sample_nature.id

                    sample_type = SampleType.query.filter_by(name=row[9]).first()
                    sample.sample_type_id = sample_type.id

                    support = Support.query.filter_by(name=row[13]).first()
                    sample.support_id = support.id

                    jonc_type = JoncType.query.filter_by(name=row[14]).first()
                    sample.jonc_type_id = jonc_type.id

                    mesure = Mesure.query.filter_by(name=row[17]).first()
                    sample.mesure_id = mesure.id

                    sample.code = row[7]
                    sample.date = str(row[10])
                    sample.technique = row[11]
                    sample.site = row[12]
                    sample.status = 0

                    patient.samples.append(sample)
                    generateCode(sample, r + 1)

                    print(str(sample.bio_code))
                order.patients.append(patient)
                db.session.commit()
        # and check sample id if already in db

        url = documents.url(filename)
        document = Document(name=filename, url=url)
        order.documents.append(document)
        db.session.add(document)
        db.session.commit()
        flash(_('Fichier importé avec succes!'))
        return redirect(url_for('order.detail', id=order.id))
    return render_template('order/import.html', order=order)


@bp.route('/order/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    order = Order.query.get(id)
    form = OrderForm(obj=order)
    form.customer.choices = [(c.id, c.display_as) for c in Customer.query.all()]
    form.project.choices = [(c.id, c.title) for c in Project.query.all()]
    form.temperature.choices = [(c.id, c.name) for c in Temperature.query.all()]

    if form.validate_on_submit():

        if 'file' in request.files:
            file = request.files['file']
            order.file_name = documents.save(file)
            order.file_url = documents.url(order.file_name)

        order.customer_id = form.project.data
        order.project_id = form.project.data
        order.first_name = form.first_name.data
        order.last_name = form.last_name.data
        order.telephone = form.telephone.data
        order.send_date = form.send_date.data
        order.temperature_id = form.temperature.data
        order.nbr_pack = form.nbr_pack.data
        db.session.commit()
        flash(_('Modification effectuée avec succèss!!'))
        return redirect(url_for('order.detail', id=order.id))
    form.customer.data = order.project.customer.id
    form.project.data = order.project_id
    form.first_name.data = order.first_name
    form.last_name.data = order.last_name
    form.telephone.data = order.telephone
    form.send_date.data = order.send_date
    form.receive_date.data = order.receive_date
    form.nbr_pack.data = order.nbr_pack
    form.temperature.data = order.temperature_id

    return render_template('order/form.html', form=form)


@bp.route('/order/process/<int:id>', methods=['GET', 'POST'])
@login_required
def process(id):
    order = Order.query.get(id)
    return render_template('order/detail.html', order=order)


@bp.route('/order/addtolist/<int:id>', methods=['GET'])
@login_required
def addtolist(id):
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    sample = Sample.query.get_or_404(id)
    basket.samples.append(sample)
    sample.basket_id = basket.id
    db.session.commit()
    return redirect(url_for('order.detail', id=sample.patient.order_id))


@bp.route('/order/removefromlist/<int:id>', methods=['GET'])
@login_required
def removefromlist(id):
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    sample = Sample.query.get(id)
    basket.samples.remove(sample)
    sample.basket_id = 0
    db.session.commit()
    return redirect(url_for('order.detail', id=sample.patient.order_id))


@bp.route('/order/add_all/<int:id>', methods=['GET'])
@login_required
def add_all(id):
    order = Order.query.get(id)
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    for patient in order.patients:
        for sample in patient.samples:
            basket.samples.append(sample)
            sample.basket_id = basket.id
            db.session.commit()
    return redirect(url_for('order.detail', id=id))


@bp.route('/order/remove_all/<int:id>', methods=['GET'])
@login_required
def remove_all(id):
    order = Order.query.get(id)
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    for patient in order.patients:
        for sample in patient.samples:
            basket.samples.remove(sample)
            sample.basket_id = 0
            db.session.commit()
    return redirect(url_for('order.detail', id=id))


def get_order_code():
    size = len(Order.query.all()) + 1
    num = str(size).zfill(5)
    return num


def get_bio_code(s):
    size = len(Patient.query.all()) + 1
    num = s + str(size).zfill(10)
    return num


def generateCode(s, index):
    jonc_type_str = ''
    if s.jonc_type:
        jonc_type_str = str(s.jonc_type.siggle)
    s.code = str(s.number) + '-' + str(s.sample_nature.siggle) + str(index) + '-' + jonc_type_str
    db.session.commit()
    # 3SURur2 - fn - rouge
    return s
