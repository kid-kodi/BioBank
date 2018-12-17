from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.role.forms import RoleForm
from app.models import Role, Category
from app.translate import translate
from app.role import bp


@bp.route('/role', methods=['GET', 'POST'])
@login_required
def index():
    roles = Role.query.all()
    return render_template('role/index.html', roles=roles)


@bp.route('/role/add', methods=['GET', 'POST'])
@login_required
def add():
    form = RoleForm()
    if form.validate_on_submit():
        role = Role(name=form.name.data, description=form.description.data)
        db.session.add(role)
        db.session.commit()
        flash(_('Nouvelle etude ajouté avec succèss!'))
        return redirect(url_for('role.detail', id=role.id))
    return render_template('role/form.html', form=form)


@bp.route('/role/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    role = Role.query.get(id)
    form = RoleForm()
    if form.validate_on_submit():
        role.name = form.name.data
        role.description = form.description.data
        db.session.commit()
        flash(_('Les informations ont été modifiées avec succèss'))
        return redirect(url_for('role.detail', id=role.id))

    form.name.data   = role.name
    form.description.data = role.description
    return render_template('role/form.html', form=form)


@bp.route('/role/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    role = Role.query.get(id)
    return render_template('role/detail.html', role=role)
