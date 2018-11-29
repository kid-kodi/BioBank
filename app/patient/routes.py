from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db, excel
from app.patient.forms import PatientForm, SearchForm
from app.models import Patient, Origin, Project, Order, SampleType, Mesure, TubeType, SampleNature, JoncType, Sample
from app.translate import translate
from app.patient import bp


@bp.route('/patient', methods=['GET', 'POST'])
@login_required
def index():
    pagination = []
    search_form = SearchForm()
    page = request.args.get('page', 1, type=int)
    if search_form.validate_on_submit():
        code = search_form.code.data
        if code != '':
            pagination = Patient.query.filter_by(code=code) \
                .order_by(Patient.created_at.desc()).paginate(
                page, per_page=current_app.config['FLASK_PER_PAGE'],
                error_out=False)
        else:
            pagination = Patient.query \
                .order_by(Patient.created_at.desc()).paginate(
                page, per_page=current_app.config['FLASK_PER_PAGE'],
                error_out=False)
    else:
        pagination = Patient.query \
            .order_by(Patient.created_at.desc()).paginate(
            page, per_page=current_app.config['FLASK_PER_PAGE'],
            error_out=False)
    patients = pagination.items
    return render_template('patient/index.html',
                           patients=patients, pagination=pagination,
                           title="patient", search_form=search_form)


@bp.route('/patient/add', methods=['GET', 'POST'])
@bp.route('/order/<int:order_id>/patient/add', methods=['GET', 'POST'])
@login_required
def add(order_id=0):
    order = None
    if order_id != 0:
        order = Order.query.get(order_id)
    form = PatientForm()
    form.order.choices = [(c.id, c.serial) for c in Order.query.all()]
    for entry in form.samples.entries:
        entry.sample_type.choices = [(c.id, c.name) for c in SampleType.query.all()]
        entry.mesure.choices = [(c.id, c.name) for c in Mesure.query.all()]
        entry.tube_type.choices = [(c.id, c.name) for c in TubeType.query.all()]
        entry.sample_nature.choices = [(c.id, c.name) for c in SampleNature.query.all()]
        entry.jonc_type.choices = [(c.id, c.name) for c in JoncType.query.all()]

    if form.validate_on_submit():
        patient = Patient(bio_code=get_bio_code('HU'), order_id=order_id, origin_id=1, code=form.code.data,
                          sexe=form.sexe.data, birthday=form.birthday.data, age=form.age.data, city=form.city.data,
                          job=form.job.data,
                          clinical_data=form.clinical_data.data)
        db.session.add(patient)
        db.session.commit()

        for s in form.samples.entries:
            print(int(s.number.data))
            for r in range(int(s.number.data)):
                sample = Sample()
                sample.origin_id = s.patient.origin_id
                sample.code = s.code.data
                sample.technique = s.technique.data
                sample.results = s.results.data
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
                generateCode(sample, r + 1)

        flash(_('Nouveau patient ajouté avec succèss!'))
        return redirect(url_for('patient.add', order_id=order_id))
    form.order.data = order_id
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
        patient.age = form.age.data
        patient.city = form.city.data
        patient.job = form.job.data
        patient.clinical_data = form.clinical_data.data
        db.session.commit()
        flash(_('Les informations ont été modifiées avec succèss'))
        return redirect(url_for('patient.index'))

    form.order.data = patient.order_id
    form.code.data = patient.code
    form.sexe.data = patient.sexe
    form.birthday.data = patient.birthday
    form.clinical_data.data = patient.clinical_data
    form.age.data = patient.age
    form.age.data = patient.age
    form.job.data = patient.job
    form.city.data = patient.city
    return render_template('patient/form.html', form=form)


@bp.route('/patient/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    patient = Patient.query.get(id)
    return render_template('patient/detail.html', patient=patient)


@bp.route("/patient/export", methods=['GET'])
@login_required
def export_data():
    return excel.make_response_from_tables(db.session, [Patient], "xls", file_name="export_data")


@bp.route("/patient/custom_export", methods=['GET'])
def docustomexport():
    query_sets = Patient.query.all()
    for row in query_sets:
        print(row.__dict__)
    column_names = ['id', 'serial', '', '', '']
    return excel.make_response_from_query_sets(query_sets, column_names, "xls", file_name="export_data")


@bp.route("/patient/import", methods=['GET', 'POST'])
@login_required
def import_data():
    if request.method == 'POST':
        # if request.form.get('is_delete') is True:
        Patient.query.delete()

        def patient_init_func(row):
            p = Patient(age=row['age'], bio_code=row['bio_code'], birthday=row['birthday'],
                        clinical_data=row['clinical_data'], code=row['code'], id=row['id'], order_id=row['order_id'],
                        origin_id=row['origin_id'], sexe=row['sexe'])
            return p

        request.save_book_to_database(
            field_name='file', session=db.session,
            tables=[Patient],
            initializers=[patient_init_func])
        return redirect(url_for('.index'))
    return render_template('patient/import.html')


def get_bio_code(s):
    size = len(Patient.query.all()) + 1
    num = s + str(size).zfill(10)
    return num


def generateCode(s, index):
    s.code = str(s.number) + '-' + str(s.sample_nature.siggle) + str(index) + '-' + str(s.jonc_type.siggle)
    db.session.commit()
    # 3SURur2 - fn - rouge
    return s
