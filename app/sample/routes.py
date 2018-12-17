from datetime import datetime
from flask import render_template, make_response, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db, excel
from app.sample.forms import SampleForm, SearchForm
from app.models import Sample, Origin, Sample, Project, Order, SampleType, Mesure, Support, Patient, Basket, \
    SampleNature, JoncType
from app.translate import translate
from app.sample import bp
import pdfkit


@bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    pagination = []
    search_form = SearchForm()
    search_form.sample_type_id.choices = [(c.id, c.name) for c in SampleType.query.all()]
    search_form.sample_type_id.choices.append((0, "Choisir un type"))
    search_form.origin_id.choices = [(c.id, c.name) for c in Origin.query.all()]
    search_form.origin_id.choices.append((0, "Choisir une origine"))
    page = request.args.get('page', 1, type=int)
    q = db.session.query(Sample)
    if search_form.validate_on_submit():
        if search_form.code.data != '':
            q = q.filter_by(code=search_form.code.data)
        if search_form.sample_type_id.data != 0:
            q = q.filter_by(sample_type_id=search_form.sample_type_id.data)
        if search_form.origin_id.data != 0:
            q = q.filter_by(origin_id=search_form.origin_id.data)

        pagination = q.order_by(Sample.created_at.desc()).paginate(
            page, per_page=current_app.config['FLASK_PER_PAGE'],
            error_out=False)
    else:
        pagination = q.order_by(Sample.created_at.desc()).paginate(
            page, per_page=current_app.config['FLASK_PER_PAGE'],
            error_out=False)
    samples = pagination.items
    return render_template('sample/search.html',
                           samples=samples, pagination=pagination,
                           title="echantillon", search_form=search_form)


@bp.route('/sample', methods=['GET', 'POST'])
@login_required
def index():
    samples = Sample.query.all()
    return render_template('sample/index.html', samples=samples)


@bp.route('/sample/add', methods=['GET', 'POST'])
@login_required
def add():
    form = SampleForm()
    form.patient.choices = [(c.id, c.code) for c in Patient.query.all()]
    form.sample_nature.choices = [(c.id, c.name) for c in SampleNature.query.all()]
    form.sample_type.choices = [(c.id, c.name) for c in SampleType.query.all()]
    form.support.choices = [(c.id, c.name) for c in Support.query.all()]
    form.jonc_type.choices = [(c.id, c.name) for c in JoncType.query.all()]
    form.mesure.choices = [(c.id, c.name) for c in Mesure.query.all()]

    if form.validate_on_submit():
        for r in range(int(form.number.data)):
            print(form.number.data)
            sample = Sample()
            sample.code = form.code.data
            sample.technique = form.technique.data
            sample.results = form.results.data
            sample.patient_id = form.patient.data
            sample.sample_nature_id = form.sample_nature.data
            sample.sample_type_id = form.sample_type.data
            sample.support_id = form.support.data
            sample.jonc_type_id = form.jonc_type.data
            sample.mesure_id = form.mesure.data
            sample.volume = form.volume.data
            sample.site = form.site.data
            sample.number = form.number.data
            sample.date = form.date.data
            sample.status = 0
            db.session.add(sample)
            db.session.commit()
            generateCode(sample, r + 1)
        flash(_('Nouveau prélèvement ajouté avec succèss!'))
        return redirect(url_for('sample.index'))
    return render_template('sample/form.html', form=form)


@bp.route('/sample/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    sample = Sample.query.get(id)
    form = SampleForm(obj=sample)
    form.patient.choices = [(c.id, c.code) for c in Patient.query.all()]
    form.sample_nature.choices = [(c.id, c.name) for c in SampleNature.query.all()]
    form.sample_type.choices = [(c.id, c.name) for c in SampleType.query.all()]
    form.support.choices = [(c.id, c.name) for c in Support.query.all()]
    form.jonc_type.choices = [(c.id, c.name) for c in JoncType.query.all()]
    form.mesure.choices = [(c.id, c.name) for c in Mesure.query.all()]

    if form.validate_on_submit():
        sample.code = form.code.data
        sample.patient_id = form.patient.data
        sample.sample_nature_id = form.sample_nature.data
        sample.sample_type_id = form.sample_type.data
        sample.support_id = form.support.data
        sample.jonc_type_id = form.jonc_type.data
        sample.mesure_id = form.mesure.data
        sample.volume = form.volume.data
        sample.site = form.site.data
        sample.date = form.date.data
        sample.technique = form.technique.data
        sample.results = form.results.data
        db.session.commit()
        flash(_('Les informations ont été modifiées avec succèss'))
        return redirect(url_for('sample.detail', id=sample.id))

    form.code.data = sample.code
    form.patient.data = sample.patient_id
    form.sample_nature.data = sample.sample_nature_id
    form.sample_type.data = sample.sample_type_id
    form.support.data = sample.support_id
    form.jonc_type.data = sample.jonc_type_id
    form.mesure.data = sample.mesure_id
    form.volume.data = sample.volume
    form.site.data = sample.site
    form.date.data = sample.date
    form.technique.data = sample.technique
    form.results.data = sample.results
    return render_template('sample/form.html', form=form)


@bp.route('/sample/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    sample = Sample.query.get(id)
    return render_template('sample/detail.html', sample=sample)


@bp.route("/sample/export", methods=['GET'])
@login_required
def export_data():
    return excel.make_response_from_tables(db.session, [Sample], "xls", file_name="export_data")


@bp.route("/sample/custom_export", methods=['GET'])
def docustomexport():
    query_sets = Sample.query.all()
    column_names = ['id', 'serial', 'code', 'sample_nature_id', 'sample_type_id']
    for key in query_sets.columns:
        column_names.append(key)
    return excel.make_response_from_query_sets(query_sets, column_names, "xls", file_name="export_data")


@bp.route("/sample/import", methods=['GET', 'POST'])
@login_required
def import_data():
    if request.method == 'POST':
        # if request.form.get('is_delete') is True:
        Sample.query.delete()

        def sample_init_func(row):
            p = Sample(code=row['code'], date=row['date'], jonc_type_id=row['jonc_type_id'],
                       mesure_id=row['mesure_id'], parent_id=row['parent_id'], patient_id=row['patient_id'],
                       sample_nature_id=row['sample_nature_id'], sample_type_id=row['sample_type_id'],
                       status=row['status'], technique=row['technique'], support_id=row['support_id'],
                       volume=row['volume'], origin_id=row['origin_id'], )
            return p

        request.save_book_to_database(
            field_name='file', session=db.session,
            tables=[Sample],
            initializers=[sample_init_func])
        return redirect(url_for('.search'))
    return render_template('sample/import.html')


@bp.route('/sample/addtolist/<int:id>', methods=['GET'])
@login_required
def addtolist(id):
    basket = Basket.query.first()
    sample = Sample.query.get_or_404(id)
    basket.samples.append(sample)
    sample.basket_id = basket.id
    db.session.commit()
    return redirect(url_for('sample.search'))


@bp.route('/sample/removefromlist/<int:id>', methods=['GET'])
@login_required
def removefromlist(id):
    basket = Basket.query.first()
    sample = Sample.query.get(id)
    basket.samples.remove(sample)
    sample.basket_id = 0
    db.session.commit()
    return redirect(url_for('sample.search'))


@bp.route('/sample/<int:id>/print', methods=['GET'])
@login_required
def print(id):
    sample = Sample.query.get(id)
    html = render_template('_bar_code.html', sample=sample)
    pdf = pdfkit.from_string(html, False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=code.pdf'
    return response


@bp.route('/sample/print_selected', methods=['GET', 'POST'])
@login_required
def print_selected(data):
    all_args = request.args.to_dict()
    print(all_args)
    sample = []
    html = render_template('_bar_code.html', sample=sample)
    pdf = pdfkit.from_string(html, False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=code.pdf'
    return response


@bp.route('/sample/print', methods=['GET', 'POST'])
@login_required
def print_to():
    data = request.get_json()
    ids = data['items']
    samples = []
    for id in ids:
        _sample = Sample.query.get(int(id))
        samples.append(_sample)

    #for value in samples:
        #print(value)
    # Make a PDF straight from HTML in a string.
    return jsonify({'samples': [sample.to_json() for sample in samples]})


def get_bio_code(s):
    size = len(Sample.query.all()) + 1
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
