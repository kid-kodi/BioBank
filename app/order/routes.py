from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.order.forms import OrderForm
from app.models import Order, Customer, Project, Patient, Sample, Origin, SampleType, Mesure, TubeType
from app.translate import translate
from app.order import bp


@bp.route('/order', methods=['GET', 'POST'])
@login_required
def index():
    orders = Order.query.all()
    return render_template('order/index.html', orders=orders)


@bp.route('/order/add', methods=['GET', 'POST'])
@login_required
def add():
    form = OrderForm()
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
        order.serial = get_order_code()
        order.project_id = form.project.data
        order.firstname = form.firstname.data
        order.lastname = form.lastname.data
        order.telephone = form.telephone.data
        order.transport_date = form.transport_date.data
        order.temperature = form.temperature.data
        order.timestamp = datetime.utcnow()
        order.user_id = current_user.id

        patient = Patient(origin_id=form.origin.data,
                          code=form.code.data, sexe=form.sexe.data, birthday=form.birthday.data)
        for s in form.samples.entries:
            sample = Sample()
            sample.serial = get_bio_code()
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
        return redirect(url_for('order.index'))
    return render_template('order/form.html', form=form)


@bp.route('/order/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    order = Order.query.get(id)
    return render_template('order/detail.html', order=order)


@bp.route('/order/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    order = Order.query.get(id)
    form = OrderForm(obj=order)
    form.origin.choices = [(c.id, c.name) for c in Origin.query.all()]
    form.customer.choices = [(c.id, c.display_as) for c in Customer.query.all()]
    form.project.choices = [(c.id, c.title) for c in Project.query.all()]

    for entry in form.samples.entries:
        entry.sample_type.choices = [(c.id, c.name) for c in SampleType.query.all()]
        entry.mesure.choices = [(c.id, c.name) for c in Mesure.query.all()]
        entry.tube_type.choices = [(c.id, c.name) for c in TubeType.query.all()]

    if form.validate_on_submit():
        order = Order()
        order.serial = get_order_code()
        order.project_id = form.project.data
        order.firstname = form.firstname.data
        order.lastname = form.lastname.data
        order.telephone = form.telephone.data
        order.transport_date = form.transport_date.data
        order.temperature = form.temperature.data
        order.timestamp = datetime.utcnow()
        order.user_id = current_user.id

        patient = Patient(origin_id=form.origin.data,
                          code=form.code.data, sexe=form.sexe.data, birthday=form.birthday.data)
        for s in form.samples.entries:
            sample = Sample()
            sample.serial = get_bio_code()
            sample.code = s.code.data
            sample.sample_type_id = s.sample_type.data
            sample.date = s.date.data
            sample.site = s.site.data
            sample.tube_type_id = s.tube_type.data
            sample.mesure_id = s.mesure.data
            sample.volume = s.volume.data
            sample.status = 0
            sample.in_basket = 0
            sample.basket_id = 0
            patient.samples.append(sample)

        order.patients.append(patient)
        db.session.add(order)
        db.session.commit()
        flash(_('Modification effectuée avec succèss!!'))
        return redirect(url_for('order.index'))
    form.customer.data = order.project.customer.id
    form.project.data = order.project_id
    form.firstname.data = order.firstname
    form.lastname.data = order.lastname
    form.telephone.data = order.telephone
    form.transport_date.data = order.transport_date
    form.temperature.data = order.temperature
    return render_template('order/form.html', form=form)


def get_order_code():
    size = len(Order.query.all()) + 1
    num = str(size).zfill(5)
    return num


def get_bio_code():
    size = len(Sample.query.all()) + 1
    num = str(size).zfill(5)
    return num