from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.technique.forms import TechniqueForm
from app.models import Technique, Category
from app.translate import translate
from app.technique import bp


@bp.route('/technique', methods=['GET', 'POST'])
@login_required
def index():
    techniques = Technique.query.all()
    return render_template('technique/list.html', techniques=techniques)


@bp.route('/technique/add', methods=['GET', 'POST'])
@login_required
def add():
    form = TechniqueForm()
    if form.validate_on_submit():
        technique = Technique(name=form.name.data, category=form.category.data, out_number=form.out_number.data,
                              in_number=form.in_number.data, description=form.description.data)
        db.session.add(technique)
        db.session.commit()
        flash(_('Nouvelle etude ajouté avec succèss!'))
        return redirect(url_for('technique.detail', id=technique.id))
    return render_template('technique/form.html', form=form)


@bp.route('/technique/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    technique = Technique.query.get(id)
    form = TechniqueForm()
    if form.validate_on_submit():
        technique.name = form.name.data
        technique.category = form.category.data
        technique.in_number = form.in_number.data
        technique.out_number = form.out_number.data
        technique.description = form.description.data
        db.session.commit()
        flash(_('Les informations ont été modifiées avec succèss'))
        return redirect(url_for('technique.detail', id=technique.id))

    form.name.data = technique.name
    form.category.data = technique.category
    form.in_number.data = technique.in_number
    form.out_number.data = technique.out_number
    return render_template('technique/form.html', form=form)


@bp.route('/technique/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    technique = Technique.query.get(id)
    return render_template('technique/detail.html', technique=technique)
