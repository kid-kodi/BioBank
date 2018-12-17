from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db, excel
from app.support.forms import SupportForm, SearchForm
from app.models import Support, Support
from app.translate import translate
from app.support import bp


@bp.route('/support', methods=['GET', 'POST'])
@login_required
def index():
    pagination = []
    search_form = SearchForm()
    page = request.args.get('page', 1, type=int)
    if search_form.validate_on_submit():
        name = search_form.name.data
        if name != '':
            pagination = Support.query.filter_by(name=name) \
                .order_by(Support.created_at.desc()).paginate(
                page, per_page=current_app.config['FLASK_PER_PAGE'],
                error_out=False)
        else:
            pagination = Support.query \
                .order_by(Support.created_at.desc()).paginate(
                page, per_page=current_app.config['FLASK_PER_PAGE'],
                error_out=False)
    else:
        pagination = Support.query \
            .order_by(Support.created_at.desc()).paginate(
            page, per_page=current_app.config['FLASK_PER_PAGE'],
            error_out=False)
    list = pagination.items
    return render_template('support/list.html',
                           list=list, pagination=pagination,
                           title="equipment", search_form=search_form)


@bp.route('/support/add', methods=['GET', 'POST'])
@login_required
def add():
    add = True
    form = SupportForm()
    if form.validate_on_submit():
        support = Support(name=form.name.data,
                                       siggle=form.siggle.data,
                                       volume=form.volume.data,
                                       description=form.description.data,
                                       created_at=datetime.utcnow(),
                                       created_by=current_user.id)
        db.session.add(support)
        db.session.commit()
        flash(_('Data saved!'))
        return redirect(url_for('support.index'))
    return render_template('support/form.html', action="Add",
                           add=add, form=form,
                           title="Add support")


@bp.route('/support/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    add = False
    support = Support.query.get_or_404(id)
    form = SupportForm(obj=support)
    if form.validate_on_submit():
        support.name = form.name.data
        support.siggle = form.siggle.data
        support.volume = form.volume.data
        support.description = form.description.data
        db.session.commit()
        flash('You have successfully edited the support.')

        # redirect to the bps page
        return redirect(url_for('support.index'))

    form.name.data = support.name
    form.siggle.data = support.siggle
    form.volume.data = support.volume
    form.description.data = support.description
    return render_template('support/form.html', action="Edit",
                           add=add, form=form,
                           support=support, title="Edit support")


@bp.route('/support/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    support = Support.query.get_or_404(id)
    return render_template('support/detail.html', support=support)


@bp.route('/support/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    support = Support.query.get_or_404(id)
    db.session.delete(support)
    db.session.commit()
    flash('You have successfully deleted the support.')

    # redirect to the bps page
    return redirect(url_for('support.index'))


@bp.route("/support/export", methods=['GET'])
@login_required
def export_data():
    return excel.make_response_from_tables(db.session, [Support], "xls", file_name="export_data")


@bp.route("/support/import", methods=['GET', 'POST'])
@login_required
def import_data():
    if request.method == 'POST':
        def support_init_func(row):
            p = Support(name=row['Nom'], siggle=row['Siggle'],
                         volume=row['Volume'], description=row['Description'])
            return p

        request.save_book_to_database(
            field_name='file', session=db.session,
            tables=[Support],
            initializers=[support_init_func])
        return redirect(url_for('.handson_table'), code=302)
    return render_template('support/import.html')


@bp.route("/support/download", methods=['GET'])
@login_required
def download():
    query_sets = Support.query.filter_by(id=1).all()
    column_names = ['name', 'siggle', 'volume', 'desqcription']
    return excel.make_response_from_query_sets(query_sets, column_names, "xls", file_name="template")
