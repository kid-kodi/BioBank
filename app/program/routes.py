from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.program.forms import ProgramForm
from app.models import Program, Subject
from app.translate import translate
from app.program import bp


@bp.route('/program', methods=['GET', 'POST'])
@login_required
def index():
    programs = Program.query.all()
    return render_template('program/index.html', programs=programs)


@bp.route('/program/add', methods=['GET', 'POST'])
@login_required
def add():
    form = ProgramForm()
    form.subject.choices = [(c.id, c.name) for c in Subject.query.all()]
    if form.validate_on_submit():
        program = Program(subject_id=form.subject.data, name=form.name.data, description=form.description.data)
        db.session.add(program)
        db.session.commit()
        flash(_('Nouveau program ajouté avec succèss!'))
        return redirect(url_for('program.detail', id=program.id))
    return render_template('program/form.html', form=form)


@bp.route('/program/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    program = Program.query.get(id)
    form = ProgramForm()
    form.subject.choices = [(c.id, c.name) for c in Subject.query.all()]
    if form.validate_on_submit():
        program.subject_id = form.subject.data
        program.name = form.name.data
        program.description = form.description.data
        db.session.commit()
        flash(_('Les informations ont été modifiées avec succèss'))
        return redirect(url_for('program.detail', id=program.id))

    form.subject.data = program.subject_id
    form.name.data = program.name
    form.description.data = program.description
    return render_template('progamme/form.html', form=form)


@bp.route('/program/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    program = Program.query.get(id)
    return render_template('program/detail.html', program=program)
