from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db, images
from app.order.forms import OrderForm
from app.models import Order, Customer, Project, Patient, Sample, Origin, SampleType, Mesure, TubeType, SampleNature, \
    JoncType, Temperature
from app.translate import translate
from app.order import bp


@bp.route('/order', methods=['GET', 'POST'])
@login_required
def index():
    orders = Order.query.all()
    return render_template('order/index.html', orders=orders)


@bp.route('/order/add', methods=['GET', 'POST'])
@bp.route('/project/<int:project_id>/order/add', methods=['GET', 'POST'])
@login_required
def add(project_id):
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
        order.serial = get_order_code()
        order.project_id = form.project.data
        order.firstname = form.firstname.data
        order.lastname = form.lastname.data
        order.telephone = form.telephone.data
        order.transport_date = form.transport_date.data
        order.temperature = form.temperature.data
        order.timestamp = datetime.utcnow()
        order.user_id = current_user.id
        db.session.add(order)
        db.session.commit()

        flash(_('Nouveau prélèvement ajouté avec succèss!'))
        return redirect(url_for('patient.add', order_id=order.id))

    return render_template('order/form.html', form=form, project=project)


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
    form.customer.choices = [(c.id, c.display_as) for c in Customer.query.all()]
    form.project.choices = [(c.id, c.title) for c in Project.query.all()]
    form.temperature.choices = [(c.id, c.name) for c in Temperature.query.all()]

    if form.validate_on_submit():
        order.customer_id = form.project.data
        order.project_id = form.project.data
        order.firstname = form.firstname.data
        order.lastname = form.lastname.data
        order.telephone = form.telephone.data
        order.transport_date = form.transport_date.data
        order.temperature = form.temperature.data
        db.session.commit()
        flash(_('Modification effectuée avec succèss!!'))
        return redirect(url_for('patient.add', order_id=order.id))
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


