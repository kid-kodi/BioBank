from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.subject.forms import SubjectForm
from app.models import Subject, Study
from app.translate import translate
from app.subject import bp


@bp.route('/subject', methods=['GET', 'POST'])
@login_required
def index():
    subjects = Subject.query.all()
    return render_template('subject/index.html', subjects=subjects)


@bp.route('/subject/add', methods=['GET', 'POST'])
@login_required
def add():
    form = SubjectForm()
    form.study.choices = [(c.id, c.name) for c in Study.query.all()]
    if form.validate_on_submit():
        subject = Subject(study_id=form.study.data, name=form.name.data, description=form.description.data)
        db.session.add(subject)
        db.session.commit()
        flash(_('Nouvelle thématique ajouté avec succèss!'))
        return redirect(url_for('subject.detail', id=subject.id))
    return render_template('subject/form.html', form=form)


@bp.route('/subject/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    subject = Subject.query.get(id)
    form = SubjectForm()
    form.study.choices = [(c.id, c.name) for c in Study.query.all()]
    if form.validate_on_submit():
        subject.study_id= form.study.data
        subject.name = form.name.data
        subject.description = form.description.data
        db.session.commit()
        flash(_('Les informations ont été modifiées avec succèss'))
        return redirect(url_for('subject.detail', id=subject.id))

    form.study.data   = subject.study_id
    form.name.data   = subject.name
    form.description.data = subject.description
    return render_template('subject/form.html', form=form)


@bp.route('/subject/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    subject = Subject.query.get(id)
    return render_template('subject/detail.html', subject=subject)
