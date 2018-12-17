import copy
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.aliquot.forms import AliquotForm
from app.models import Hole, Sample, Basket, Box, Aliquot, AliquotItem, Mesure, Support
from app.translate import translate
from app.aliquot import bp


@bp.route('/aliquot', methods=['GET', 'POST'])
@login_required
def index():
    aliquots = Aliquot.query.all()
    print(aliquots)
    return render_template('aliquot/list.html', aliquots=aliquots)


@bp.route('/aliquot/add', methods=['GET', 'POST'])
@login_required
def add():
    form = AliquotForm()
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    form.support.choices = [(c.id, c.name) for c in Support.query.all()]
    form.samples.choices = [(c.id, str(c.patient.bio_code + ' ' + c.code)) for c in
                            basket.samples.filter_by(parent_id=None).all()]
    form.mesure.choices = [(c.id, c.name) for c in Mesure.query.all()]
    if form.validate_on_submit():
        aliquot = Aliquot()
        aliquot.serial = datetime.utcnow().strftime("%d%m%Y%H%M%S")
        aliquot.support_id = form.support.data
        aliquot.volume = form.volume.data
        aliquot.mesure_id = form.mesure.data
        aliquot.status = 0
        aliquot.timestamp = datetime.utcnow()
        aliquot.created_by = current_user.id
        for sample_id in form.samples.data:
            sample = Sample.query.get(sample_id)
            aliquot_item = AliquotItem()
            aliquot_item.sample_id = sample_id
            aliquot_item.support_id = form.support.data
            aliquot_item.mesure_id = form.mesure.data
            aliquot_item.nbr_aliquot = int(sample.volume) / int(form.volume.data)
            aliquot_item.volume_by_aliquot = form.volume.data
            aliquot_item.status = 0
            aliquot_item.created_by = current_user.id
            aliquot_item.timestamp = datetime.utcnow()
            aliquot.aliquot_items.append(aliquot_item)
            db.session.add(aliquot)
            db.session.commit()
        flash(_('Enregistrement effectué avec succèss'))
        return redirect(url_for('aliquot.index'))
    return render_template('aliquot/form.html', form=form, basket=basket)


@bp.route('/aliquot/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    aliquot = Aliquot.query.get(id)
    return render_template('aliquot/detail.html', aliquot=aliquot)


@bp.route('/aliquot/proceed/<int:id>', methods=['GET', 'POST'])
@login_required
def proceed(id):
    aliquot = Aliquot.query.get(id)
    for aliquot_items in aliquot.aliquot_items:
        _sample = copy.deepcopy(aliquot_items.sample)
        for num in range(aliquot_items.nbr_aliquot):
            sample = Sample()
            sample.code = _sample.code
            sample.parent_id = aliquot_items.sample_id
            sample.technique = _sample.technique
            sample.patient_id = _sample.patient_id
            sample.sample_nature_id = _sample.sample_nature_id
            sample.sample_type_id = _sample.sample_type_id
            sample.support_id = _sample.support_id
            sample.jonc_type_id = _sample.jonc_type_id
            sample.mesure_id = _sample.mesure_id
            sample.volume = aliquot_items.volume_by_aliquot
            sample.site = _sample.site
            sample.number = num
            sample.date = _sample.date
            sample.status = 0

            db.session.add(sample)
            db.session.commit()
            generateCode(sample, num + 1)

        __sample = Sample.query.get(aliquot_items.sample.id)
        __sample.volume = 0
        __sample.status = 3
        aliquot_items.status = 1
        db.session.commit()
    aliquot.status = 1
    db.session.commit()
    flash(_('Enregistrement effectué avec succèss'))
    return redirect(url_for('aliquot.index'))


@bp.route('/aliquot/set_hole/<int:id>', methods=['GET', 'POST'])
@login_required
def set_hole(id):
    aliquot_item = AliquotItem.query.get(id)
    if request.method == 'POST':
        aliquot_item.sample_id = request.form['sample_id']
        aliquot_item.hole_id = request.form['hole_id']
        print(aliquot_item.sample_id)
        print(aliquot_item.hole_id)
        db.session.commit()
    return redirect(url_for('aliquot.detail', id=aliquot_item.aliquot.id))


def generateCode(s, index):
    jonc_type_str = ''
    if s.jonc_type:
        jonc_type_str = str(s.jonc_type.siggle)
    s.code = str(s.number) + '-' + str(s.sample_nature.siggle) + str(index) + '-' + jonc_type_str
    db.session.commit()
    # 3SURur2 - fn - rouge
    return s
