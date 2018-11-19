from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.project.forms import ProjectForm
from app.models import Project, Customer, Study, Subject, Program
from app.translate import translate
from app.project import bp


@bp.route('/project', methods=['GET', 'POST'])
@login_required
def index():
    projects = Project.query.all()
    return render_template('project/index.html', projects=projects)


@bp.route('/project/add', methods=['GET', 'POST'])
@bp.route('/customer/<int:customer_id>/project/add', methods=['GET', 'POST'])
@login_required
def add(customer_id=0):
    customer = None
    if customer_id:
        customer = Customer.query.get(customer_id)
    form = ProjectForm()
    form.customer.choices = [(c.id, c.display_as) for c in Customer.query.all()]
    form.study.choices = [(c.id, c.name) for c in Study.query.all()]
    form.subject.choices = [(c.id, c.name) for c in Subject.query.all()]
    form.program.choices = [(c.id, c.name) for c in Program.query.all()]
    if form.validate_on_submit():
        project = Project(customer_id=form.customer.data, study_id=form.study.data,
                    subject_id=form.subject.data, program_id=form.program.data,
                    title=form.title.data, description=form.description.data)
        db.session.add(project)
        db.session.commit()
        flash(_('Nouveau projetc ajouté avec succèss!'))
        return redirect(url_for('order.add', project_id=project.id))
    form.customer.data = customer_id
    return render_template('project/form.html', form=form)


@bp.route('/project/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    project = Project.query.get(id)
    form = ProjectForm()
    form.customer.choices = [(c.id, c.display_as) for c in Customer.query.all()]
    form.study.choices = [(c.id, c.name) for c in Study.query.all()]
    form.subject.choices = [(c.id, c.name) for c in Subject.query.all()]
    form.program.choices = [(c.id, c.name) for c in Program.query.all()]
    if form.validate_on_submit():
        project.customer_id = form.customer.data
        project.study_id  = form.study.data
        project.subject_id   = form.subject.data
        project.program_id    = form.program.data
        project.title   = form.title.data
        project.description  = form.description.data
        db.session.commit()
        flash(_('Les informations ont été modifiées avec succèss'))
        return redirect(url_for('project.detail', id=project.id))

    form.customer.data   = project.customer_id
    form.study.data = project.study_id
    form.subject.data  = project.subject_id
    form.program.data   = project.program_id
    form.description.data  = project.description
    form.title.data    = project.title
    return render_template('project/form.html', form=form)


@bp.route('/project/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    project = Project.query.get(id)
    return render_template('project/detail.html', project=project)
