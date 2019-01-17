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
                            basket.samples.filter_by(parent_id=None, status=3).all()]
    form.mesure.choices = [(c.id, c.name) for c in Mesure.query.all()]
    if form.validate_on_submit():
        serial = datetime.utcnow().strftime("%d%m%Y%H%M%S")
        for sample_id in form.samples.data:
            aliquot = Aliquot()
            aliquot.serial = serial
            aliquot.sample_id = sample_id
            aliquot.support_id = form.support.data
            aliquot.support_id = form.support.data
            aliquot.volume = form.volume.data
            aliquot.mesure_id = form.mesure.data
            aliquot.status = 0
            aliquot.timestamp = datetime.utcnow()
            aliquot.created_by = current_user.id
            db.session.add(aliquot)
            db.session.commit()
            for aliquot_item_num in range(aliquot.nbr_aliquot()):
                aliquot_item = AliquotItem()
                aliquot_item.aliquot_id = aliquot.id
                aliquot_item.serial = 'A' + str(aliquot_item_num)
                aliquot_item.volume = aliquot.volume / aliquot.nbr_aliquot()
                aliquot_item.status = 0
                aliquot_item.created_by = current_user.id
                aliquot_item.timestamp = datetime.utcnow()
                db.session.add(aliquot_item)
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
    for _item in range(len(aliquot.aliquot_items.all())):
        num = 0
        _sample = aliquot.sample
        _sample.status = 3
        sample = Sample()
        sample.code = _sample.code
        sample.parent_id = _sample.id
        sample.technique = _sample.technique
        sample.patient_id = _sample.patient_id
        sample.sample_nature_id = _sample.sample_nature_id
        sample.sample_type_id = _sample.sample_type_id
        sample.support_id = _sample.support_id
        sample.jonc_type_id = _sample.jonc_type_id
        sample.mesure_id = _sample.mesure_id
        sample.volume = aliquot.aliquot_items[num].volume
        sample.site = _sample.site
        sample.date = _sample.date
        sample.status = 0
        aliquot.aliquot_items[num].status = 1
        db.session.add(sample)
        db.session.commit()
        num = num + 1
        generateCode(sample, aliquot.nbr_aliquot(), num)

    __sample = Sample.query.get(_sample.id)
    __sample.volume = 0

    aliquot.status = 1
    db.session.commit()
    flash(_('Enregistrement effectué avec succèss'))
    return redirect(url_for('aliquot.index'))


@bp.route('/aliquot/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    _item = AliquotItem.query.get(id)
    if request.method == 'POST':
        _item.volume = request.form['volume']
        db.session.commit()
    return redirect(url_for('aliquot.detail', id=_item.aliquot.id))


def generateCode(s, total, index):
    jonc_type_str = ''
    if s.jonc_type:
        jonc_type_str = str(s.jonc_type.siggle)
    s.code = str(total) + '-' + str(s.sample_nature.siggle) + str(index) + '-' + jonc_type_str
    db.session.commit()
    # 3SURur2 - fn - rouge
    return s
