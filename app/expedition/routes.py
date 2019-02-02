import os
import xlrd
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, send_from_directory
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from app import db, documents
from app.expedition.forms import ExpeditionForm
from app.models import Expedition, Customer, Sample, Project, Temperature, Basket
from app.expedition import bp

basedir = ''


@bp.route('/expedition', methods=['GET', 'POST'])
@login_required
def index():
    expeditions = Expedition.query.all()
    return render_template('expedition/index.html', expeditions=expeditions)


@bp.route('/expedition/download_file/<filename>')
def download_file(filename):
    return send_from_directory(current_app.config['UPLOADS_DEFAULT_DEST'], filename, as_attachment=True)


@bp.route('/expedition/add', methods=['GET', 'POST'])
@login_required
def add():
    form = ExpeditionForm()
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    form.samples.choices = [(c.id, c.code) for c in basket.samples.filter_by(status=0).all()]
    form.customer.choices = [(c.id, c.display_as) for c in Customer.query.all()]
    form.project.choices = [(c.id, c.name) for c in Project.query.all()]
    form.temperature.choices = [(c.id, c.name) for c in Temperature.query.all()]

    if form.validate_on_submit():
        expedition = Expedition()
        expedition.serial = get_expedition_code()
        expedition.project_id = form.project.data
        expedition.first_name = form.first_name.data
        expedition.last_name = form.last_name.data
        expedition.telephone = form.telephone.data
        expedition.expedition_date = form.expedition_date.data
        expedition.temperature_id = form.temperature.data
        expedition.nbr_pack = form.nbr_pack.data
        expedition.timestamp = datetime.utcnow()
        expedition.user_id = current_user.id
        for strain_id in form.samples.data:
            strain = Sample.query.get(strain_id)
            strain.status = 10
            db.session.commit()
        expedition.status = 0
        db.session.add(expedition)
        db.session.commit()

        flash(_('Informations du dépôt enregistrées!'))
        return redirect(url_for('expedition.detail', id=expedition.id))

    return render_template('expedition/form.html', form=form)


@bp.route('/expedition/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    expedition = Expedition.query.get(id)
    return render_template('expedition/detail.html', expedition=expedition)


@bp.route('/expedition/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    expedition = Expedition.query.get(id)
    form = ExpeditionForm(obj=expedition)
    form.customer.choices = [(c.id, c.display_as) for c in Customer.query.all()]
    form.project.choices = [(c.id, c.name) for c in Project.query.all()]
    form.temperature.choices = [(c.id, c.name) for c in Temperature.query.all()]

    if form.validate_on_submit():
        expedition.project_id = form.project.data
        expedition.first_name = form.first_name.data
        expedition.last_name = form.last_name.data
        expedition.telephone = form.telephone.data
        expedition.expedition_date = form.expedition_date.data
        expedition.temperature_id = form.temperature.data
        expedition.nbr_pack = form.nbr_pack.data
        expedition.samples = basket.samples
        db.session.commit()
        flash(_('Modification effectuée avec succèss!!'))
        return redirect(url_for('expedition.detail', id=expedition.id))
    form.frame.data = expedition.frame.id
    form.first_name.data = expedition.first_name
    form.last_name.data = expedition.last_name
    form.telephone.data = expedition.telephone
    form.expedition_date.data = expedition.expedition_date
    form.nbr_pack.data = expedition.nbr_pack
    form.temperature.data = expedition.temperature_id

    return render_template('expedition/form.html', form=form)


@bp.route('/expedition/process/<int:id>', methods=['GET', 'POST'])
@login_required
def process(id):
    expedition = Expedition.query.get(id)
    return render_template('expedition/detail.html', expedition=expedition)


@bp.route('/expedition/addtolist/<int:id>', methods=['GET'])
@login_required
def addtolist(id):
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    sample = Sample.query.get_or_404(id)
    basket.samples.append(sample)
    sample.basket_id = basket.id
    db.session.commit()
    return redirect(url_for('expedition.detail', id=sample.patient.expedition_id))


@bp.route('/expedition/removefromlist/<int:id>', methods=['GET'])
@login_required
def removefromlist(id):
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    sample = Sample.query.get(id)
    basket.samples.remove(sample)
    sample.basket_id = 0
    db.session.commit()
    return redirect(url_for('expedition.detail', id=sample.patient.expedition_id))


@bp.route('/expedition/add_all/<int:id>', methods=['GET'])
@login_required
def add_all(id):
    expedition = Expedition.query.get(id)
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    for patient in expedition.patients:
        for sample in patient.samples:
            basket.samples.append(sample)
            sample.basket_id = basket.id
            db.session.commit()
    return redirect(url_for('expedition.detail', id=id))


@bp.route('/expedition/remove_all/<int:id>', methods=['GET'])
@login_required
def remove_all(id):
    expedition = Expedition.query.get(id)
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    for patient in expedition.patients:
        for sample in patient.samples:
            basket.samples.remove(sample)
            sample.basket_id = 0
            db.session.commit()
    return redirect(url_for('expedition.detail', id=id))


def get_expedition_code():
    size = len(Expedition.query.all()) + 1
    num = str(size).zfill(5)
    return num


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
