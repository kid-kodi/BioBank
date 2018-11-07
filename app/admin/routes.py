from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.study.forms import StudyForm
from app.models import Study, Category
from app.translate import translate
from app.study import bp


@bp.route('/study', methods=['GET', 'POST'])
@login_required
def index():
    studys = Study.query.all()
    return render_template('study/index.html', studys=studys)


@bp.route('/study/add', methods=['GET', 'POST'])
@login_required
def add():
    form = StudyForm()
    if form.validate_on_submit():
        study = Study(name=form.name.data, description=form.description.data)
        db.session.add(study)
        db.session.commit()
        flash(_('Nouvelle etude ajouté avec succèss!'))
        return redirect(url_for('study.detail', id=study.id))
    return render_template('study/form.html', form=form)


@bp.route('/study/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    study = Study.query.get(id)
    form = StudyForm()
    if form.validate_on_submit():
        study.name = form.name.data
        study.description = form.description.data
        db.session.commit()
        flash(_('Les informations ont été modifiées avec succèss'))
        return redirect(url_for('study.detail', id=study.id))

    form.name.data   = study.name
    form.description.data = study.description
    return render_template('study/form.html', form=form)


@bp.route('/study/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    study = Study.query.get(id)
    return render_template('study/detail.html', study=study)
