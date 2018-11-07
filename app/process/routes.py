import copy
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db, excel
from app.process.forms import ProcessForm
from app.project.forms import ProjectForm
from app.models import Process, Technique, Project, Sample, Subject, Program, Basket, Aliquot
from app.translate import translate
from app.process import bp


@bp.route('/process', methods=['GET', 'POST'])
@login_required
def index():
    processes = Aliquot.query.all()
    return render_template('process/index.html', processes=processes)


@bp.route('/process/add', methods=['GET', 'POST'])
@login_required
def add():
    form = ProcessForm()
    form.sample.choices = [(c.id, c.code) for c in Basket.query.first().samples]
    if form.validate_on_submit():
        process = Aliquot(sample_id=form.sample.data, number=form.number.data)
        db.session.add(process)
        db.session.commit()

        sample = Sample.query.get(form.sample.data)
        for x in range(int(form.number.data)):
            _sample = Sample()
            _sample.patient_id = sample.patient_id
            _sample.parent_id = sample.id
            _sample.code = sample.code + "-" + str(x)
            _sample.volume = int(sample.volume) / int(form.number.data)
            # _sample = Sample()
            # _sample.serial = get_bio_code()
            # _sample.code = s.code.data
            _sample.sample_type_id = sample.sample_type_id
            _sample.date = sample.date
            _sample.site = sample.site
            _sample.tube_type_id = sample.tube_type_id
            _sample.mesure_id = sample.mesure_id
            _sample.status = 0
            _sample.in_basket = 0
            _sample.basket_id = 0
            db.session.add(_sample)
            sample.status = 1
            db.session.commit()
        flash(_('Nouveau Client ajouté avec succèss!'))
        return redirect(url_for('process.detail', id=process.id))
    return render_template('process/form.html', form=form)


@bp.route('/process/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    process = Process.query.get(id)
    form = ProcessForm()
    form.sample.choices = [(c.id, c.code) for c in Basket.query.first().samples]
    if form.validate_on_submit():
        process.sample_id = form.sample.data
        process.number  = form.number.data
        db.session.commit()
        flash(_('Les informations ont été modifiées avec succèss'))
        return redirect(url_for('process.detail', id=process.id))

    form.sample.data   = process.sample_id
    form.number.data = process.number
    return render_template('process/form.html', form=form)


@bp.route('/process/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    process = Aliquot.query.get(id)
    return render_template('process/detail.html', process=process)


@bp.route("/process/export", methods=['GET'])
@login_required
def export_data():
    return excel.make_response_from_tables(db.session, [Process], "xls", file_name="export_data")


@bp.route("/process/import", methods=['GET', 'POST'])
@login_required
def import_data():
    if request.method == 'POST':
        def process_init_func(row):
            c = Category.query.filter_by(name=row['category']).first()
            p = Process(category=c, display_as=row['display_as'], firstname=row['firstname'],
                         lastname=row['lastname'], adresse=row['adresse'], telephone=row['telephone'], email=row['email'])
            return p

        request.save_book_to_database(
            field_name='file', session=db.session,
            tables=[Process],
            initializers=[process_init_func])
        return redirect(url_for('.handson_table'), code=302)
    return render_template('process/import.html')


@bp.route("/handson_view", methods=['GET'])
def handson_table():
    return excel.make_response_from_tables(
        db.session, [Process], 'handsontable.html')


@bp.route("/process/download", methods=['GET'])
@login_required
def download():
    query_sets = Process.query.filter_by(id=1).all()
    column_names = ['category_id', 'display_as', 'firstname', 'lastname', 'adresse', 'telephone', 'email']
    return excel.make_response_from_query_sets(query_sets, column_names, "xls", file_name="template")
