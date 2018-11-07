from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.sample.forms import PatientForm, SearchForm
from app.models import Sample, Origin, Customer, Project, Order, SampleType, Mesure, TubeType, Patient, Basket
from app.translate import translate
from app.sample import bp


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
    form = PatientForm()
    form.origin.choices = [(c.id, c.name) for c in Origin.query.all()]
    form.customer.choices = [(c.id, c.display_as) for c in Customer.query.all()]
    form.project.choices = [(c.id, c.title) for c in Project.query.all()]
    #form.order.choices = [(c.id, c.id) for c in Order.query.all()]

    for entry in form.samples.entries:
        entry.sample_type.choices = [(c.id, c.name) for c in SampleType.query.all()]
        entry.mesure.choices = [(c.id, c.name) for c in Mesure.query.all()]
        entry.tube_type.choices = [(c.id, c.name) for c in TubeType.query.all()]

    if form.validate_on_submit():
        order = Order()
        order.project_id = form.project.data
        order.firstname = form.firstname.data
        order.lastname = form.lastname.data
        order.telephone = form.telephone.data
        order.transport_date = form.transport_date.data
        order.temperature = form.temperature.data

        patient = Patient(origin_id=form.origin.data,
                          code=form.code.data, sexe=form.sexe.data, birthday=form.birthday.data)
        for s in form.samples.entries:
            sample = Sample()
            sample.code = s.code.data
            sample.sample_type_id = s.sample_type.data
            sample.date = s.date.data
            sample.site = s.site.data
            sample.tube_type_id = s.tube_type.data
            sample.mesure_id = s.mesure.data
            sample.volume = s.volume.data
            patient.samples.append(sample)

        order.patients.append(patient)
        db.session.add(order)
        db.session.commit()
        flash(_('Nouveau prélèvement ajouté avec succèss!'))
        return redirect(url_for('sample.index'))
    return render_template('sample/form.html', form=form)


@bp.route('/sample/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    sample = Sample.query.get(id)
    form = SampleForm()

    form.origin.choices = [(c.id, c.name) for c in Origin.query.all()]
    if form.validate_on_submit():
        sample.origin_id  = form.origin.data
        sample.code       = form.code.data
        sample.birthday   = form.birthday.data
        sample.display_as = form.display_as.data
        sample.firstname  = form.firstname.data
        sample.lastname   = form.lastname.data
        sample.adresse    = form.adresse.data
        sample.telephone  = form.telephone.data
        sample.email      = form.email.data
        db.session.commit()
        flash(_('Les informations ont été modifiées avec succèss'))
        return redirect(url_for('sample.detail', id=sample.id))

    form.origin.data     = sample.origin_id
    form.code.data       = sample.code
    form.birthday.data   = sample.birthday
    form.display_as.data = sample.display_as
    form.firstname.data  = sample.firstname
    form.lastname.data   = sample.lastname
    form.adresse.data    = sample.adresse
    form.telephone.data  = sample.telephone
    form.email.data      = sample.email
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
