from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.disease.forms import DiseaseForm
from app.models import Disease, Category
from app.translate import translate
from app.disease import bp


@bp.route('/disease', methods=['GET', 'POST'])
@login_required
def index():
    diseases = Disease.query.all()
    return render_template('disease/index.html', diseases=diseases)


@bp.route('/disease/add', methods=['GET', 'POST'])
@login_required
def add():
    form = DiseaseForm()
    if form.validate_on_submit():
        disease = Disease(name=form.name.data, description=form.description.data)
        db.session.add(disease)
        db.session.commit()
        flash(_('Nouvelle etude ajouté avec succèss!'))
        return redirect(url_for('disease.detail', id=disease.id))
    return render_template('disease/form.html', form=form)


@bp.route('/disease/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    disease = Disease.query.get(id)
    form = DiseaseForm()
    if form.validate_on_submit():
        disease.name = form.name.data
        disease.description = form.description.data
        db.session.commit()
        flash(_('Les informations ont été modifiées avec succèss'))
        return redirect(url_for('disease.detail', id=disease.id))

    form.name.data   = disease.name
    form.description.data = disease.description
    return render_template('disease/form.html', form=form)


@bp.route('/disease/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    disease = Disease.query.get(id)
    return render_template('disease/detail.html', disease=disease)
