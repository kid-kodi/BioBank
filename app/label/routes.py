from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.label.forms import LabelForm
from app.models import Label, Category
from app.translate import translate
from app.label import bp


@bp.route('/label', methods=['GET', 'POST'])
@login_required
def index():
    labels = Label.query.all()
    return render_template('label/index.html', labels=labels)


@bp.route('/label/add', methods=['GET', 'POST'])
@login_required
def add():
    form = LabelForm()
    if form.validate_on_submit():
        label = Label(name=form.name.data, description=form.description.data)
        db.session.add(label)
        db.session.commit()
        flash(_('Nouvelle etude ajouté avec succèss!'))
        return redirect(url_for('label.detail', id=label.id))
    return render_template('label/form.html', form=form)


@bp.route('/label/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    label = Label.query.get(id)
    form = LabelForm()
    if form.validate_on_submit():
        label.name = form.name.data
        label.description = form.description.data
        db.session.commit()
        flash(_('Les informations ont été modifiées avec succèss'))
        return redirect(url_for('label.detail', id=label.id))

    form.name.data   = label.name
    form.description.data = label.description
    return render_template('label/form.html', form=form)


@bp.route('/label/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    label = Label.query.get(id)
    return render_template('label/detail.html', label=label)
