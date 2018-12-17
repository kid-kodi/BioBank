from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db, excel
from app.sample_type.forms import SampleTypeForm, SearchForm
from app.models import SampleType
from app.translate import translate
from app.sample_type import bp


@bp.route('/sample_type', methods=['GET', 'POST'])
@login_required
def index():
    pagination = []
    search_form = SearchForm()
    page = request.args.get('page', 1, type=int)
    if search_form.validate_on_submit():
        name = search_form.name.data
        if name != '':
            pagination = SampleType.query.filter_by(name=name) \
                .order_by(SampleType.created_at.desc()).paginate(
                page, per_page=current_app.config['FLASK_PER_PAGE'],
                error_out=False)
        else:
            pagination = SampleType.query \
                .order_by(SampleType.created_at.desc()).paginate(
                page, per_page=current_app.config['FLASK_PER_PAGE'],
                error_out=False)
    else:
        pagination = SampleType.query \
            .order_by(SampleType.created_at.desc()).paginate(
            page, per_page=current_app.config['FLASK_PER_PAGE'],
            error_out=False)
    list = pagination.items
    return render_template('sample_type/list.html',
                           list=list, pagination=pagination,
                           title="type d'échantillon", search_form=search_form)


@bp.route('/sample_type/add', methods=['GET', 'POST'])
@login_required
def add():
    add = True
    form = SampleTypeForm()
    if form.validate_on_submit():
        sample_type = SampleType(name=form.name.data,
                                 siggle=form.siggle.data,
                                 description=form.description.data,
                                 created_at=datetime.utcnow(),
                                 created_by=current_user.id)
        db.session.add(sample_type)
        db.session.commit()
        flash(_('Data saved!'))
        return redirect(url_for('sample_type.index'))
    return render_template('sample_type/form.html', action="Add",
                           add=add, form=form,
                           title="Add sample_type")


@bp.route('/sample_type/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    add = False
    sample_type = SampleType.query.get_or_404(id)
    form = SampleTypeForm(obj=sample_type)
    if form.validate_on_submit():
        sample_type.name = form.name.data
        sample_type.siggle = form.siggle.data
        sample_type.description = form.description.data
        db.session.commit()
        flash('You have successfully edited the sample_type.')

        # redirect to the bps page
        return redirect(url_for('sample_type.index'))

    form.name.data = sample_type.name
    form.siggle.data = sample_type.siggle
    form.description.data = sample_type.description
    return render_template('sample_type/form.html', action="Edit",
                           add=add, form=form,
                           sample_type=sample_type, title="Edit sample_type")


@bp.route('/sample_type/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    sample_type = SampleType.query.get_or_404(id)
    return render_template('sample_type/detail.html', sample_type=sample_type)


@bp.route('/sample_type/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    sample_type = SampleType.query.get_or_404(id)
    db.session.delete(sample_type)
    db.session.commit()
    flash('You have successfully deleted the sample_type.')

    # redirect to the bps page
    return redirect(url_for('sample_type.index'))


@bp.route("/sample_type/export", methods=['GET'])
@login_required
def export_data():
    return excel.make_response_from_tables(db.session, [SampleType], "xls", file_name="export_data")


@bp.route("/sample_type/import", methods=['GET', 'POST'])
@login_required
def import_data():
    if request.method == 'POST':
        def sample_type_init_func(row):
            p = SampleType(name=row['Nom'], siggle=row['Siggle'],
                           volume=row['Volume'], description=row['Description'])
            return p

        request.save_book_to_database(
            field_name='file', session=db.session,
            tables=[SampleType],
            initializers=[sample_type_init_func])
        return redirect(url_for('.handson_table'), code=302)
    return render_template('sample_type/import.html')


@bp.route("/sample_type/download", methods=['GET'])
@login_required
def download():
    query_sets = SampleType.query.filter_by(id=1).all()
    column_names = ['name', 'siggle', 'desqcription']
    return excel.make_response_from_query_sets(query_sets, column_names, "xls", file_name="template")
