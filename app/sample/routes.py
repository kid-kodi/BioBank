from datetime import datetime
from flask import render_template, make_response, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.sample.forms import SampleForm, SearchForm
from app.models import Sample, Origin, Customer, Project, Order, SampleType, Mesure, TubeType, Patient, Basket, \
    SampleNature, JoncType
from app.translate import translate
from app.sample import bp
import pdfkit


@bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    pagination = []
    search_form = SearchForm()
    search_form.sample_type.choices = [(c.id, c.name) for c in Origin.query.all()]
    page = request.args.get('page', 1, type=int)
    if search_form.validate_on_submit():
        code = search_form.code.data
        if code != '':
            pagination = Sample.query.filter_by(code=code) \
                .order_by(Sample.created_at.desc()).paginate(
                page, per_page=current_app.config['FLASK_PER_PAGE'],
                error_out=False)
        else:
            pagination = Sample.query \
                .order_by(Sample.created_at.desc()).paginate(
                page, per_page=current_app.config['FLASK_PER_PAGE'],
                error_out=False)
    else:
        pagination = Sample.query \
            .order_by(Sample.created_at.desc()).paginate(
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
    form.tube_type.choices = [(c.id, c.name) for c in TubeType.query.all()]
    form.jonc_type.choices = [(c.id, c.name) for c in JoncType.query.all()]
    form.mesure.choices = [(c.id, c.name) for c in Mesure.query.all()]

    if form.validate_on_submit():
        sample = Sample()
        sample.serial = get_bio_code('HU')
        sample.code = form.code.data
        sample.patient_id = form.patient.data
        sample.sample_nature_id = form.sample_nature.data
        sample.sample_type_id = form.sample_type.data
        sample.tube_type_id = form.tube_type.data
        sample.jonc_type_id = form.jonc_type.data
        sample.mesure_id = form.mesure.data
        sample.volume = form.volume.data
        sample.site = form.site.data
        sample.date = form.date.data
        db.session.add(sample)
        db.session.commit()
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
    form.tube_type.choices = [(c.id, c.name) for c in TubeType.query.all()]
    form.jonc_type.choices = [(c.id, c.name) for c in JoncType.query.all()]
    form.mesure.choices = [(c.id, c.name) for c in Mesure.query.all()]

    if form.validate_on_submit():
        sample.code = form.code.data
        sample.patient_id = form.patient.data
        sample.sample_nature_id = form.sample_nature.data
        sample.sample_type_id = form.sample_type.data
        sample.tube_type_id = form.tube_type.data
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
    form.tube_type.data = sample.tube_type_id
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


@bp.route('/sample/addtolist/<int:id>', methods=['GET'])
@login_required
def addtolist(id):
    basket = Basket.query.first()
    sample = Sample.query.get_or_404(id)
    basket.samples.append(sample)
    sample.basket_id = basket.id
    db.session.commit()
    return redirect(url_for('sample.index'))


@bp.route('/sample/removefromlist/<int:id>', methods=['GET'])
@login_required
def removefromlist(id):
    basket = Basket.query.first()
    sample = Sample.query.get(id)
    basket.samples.remove(sample)
    sample.basket_id = 0
    db.session.commit()
    return redirect(url_for('sample.index'))


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


def get_bio_code(s):
    size = len(Sample.query.all()) + 1
    num = s + str(size).zfill(10)
    return num