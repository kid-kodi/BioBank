from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.store.forms import StoreForm
from app.models import Hole, Sample, Basket, Box, Store, StoreItem
from app.translate import translate
from app.store import bp


@bp.route('/store', methods=['GET', 'POST'])
@login_required
def index():
    stores = Store.query.all()
    return render_template('store/list.html', stores=stores)


@bp.route('/store/add', methods=['GET', 'POST'])
@login_required
def add():
    form = StoreForm()
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    form.samples.choices = [(c.id, c.code) for c in basket.samples.filter_by(status=0).all()]
    form.box.choices = [(c.id, c.name) for c in Box.query.all()]
    if form.validate_on_submit():
        box = Box.query.get(form.box.data)
        store = Store()
        store.serial = datetime.utcnow().strftime("%d%m%Y%H%M%S")
        store.box_id = form.box.data
        store.status = 0
        store.timestamp = datetime.utcnow()
        store.created_by = current_user.id
        for sample_id in form.samples.data:
            hole = box.holes.filter_by(status=0).first()
            store_item = StoreItem()
            store_item.sample_id = sample_id
            store_item.hole_id = hole.id
            store_item.status = 0
            store_item.created_by = current_user.id
            store_item.timestamp = datetime.utcnow()
            store.store_items.append(store_item)
        db.session.add(store)
        db.session.commit()
        # box = Box.query.get(form.box.data)
        # sampleIds = form.samples.data
        # print(sampleIds)
        # for sid in sampleIds:
        #     sample = Sample.query.get_or_404(sid)
        #     hole = box.holes.filter_by(status=0).first()
        #     hole.status = 1
        #     sample.status = 1
        #     basket.samples.remove(sample)
        #     sample.holes.append(hole)
        #     db.session.add(sample)
        #     db.session.commit()
        flash(_('Enregistrement effectué avec succèss'))
        return redirect(url_for('store.index'))
    return render_template('store/form.html', form=form, basket=basket)


@bp.route('/store/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    store = Store.query.get(id)
    holes = store.box.holes.filter_by(status=0).all()
    return render_template('store/detail.html', store=store, holes=holes)


@bp.route('/store/proceed/<int:id>', methods=['GET', 'POST'])
@login_required
def proceed(id):
    basket = Basket.query.filter_by(created_by=current_user.id).first()
    store = Store.query.get(id)
    for store_items in store.store_items:
        sample = store_items.sample
        hole = store_items.hole
        hole.status = 1
        sample.status = 1
        basket.samples.remove(sample)
        sample.holes.append(hole)
        store_items.status = 1
        db.session.commit()
    store.status = 1
    db.session.commit()
    flash(_('Enregistrement effectué avec succèss'))
    return redirect(url_for('store.index'))


@bp.route('/store/set_hole/<int:id>', methods=['GET', 'POST'])
@login_required
def set_hole(id):
    store_item = StoreItem.query.get(id)
    if request.method == 'POST':
        store_item.sample_id = request.form['sample_id']
        store_item.hole_id = request.form['hole_id']
        print(store_item.sample_id)
        print(store_item.hole_id)
        db.session.commit()
    return redirect(url_for('store.detail', id=store_item.store.id))
