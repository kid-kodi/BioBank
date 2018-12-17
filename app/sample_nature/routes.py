from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db, excel
from app.sample_nature.forms import SampleNatureForm, SearchForm
from app.models import SampleNature
from app.translate import translate
from app.sample_nature import bp


@bp.route('/sample_nature', methods=['GET', 'POST'])
@login_required
def index():
    pagination = []
    search_form = SearchForm()
    page = request.args.get('page', 1, type=int)
    if search_form.validate_on_submit():
        name = search_form.name.data
        if name != '':
            pagination = SampleNature.query.filter_by(name=name) \
                .order_by(SampleNature.created_at.desc()).paginate(
                page, per_page=current_app.config['FLASK_PER_PAGE'],
                error_out=False)
        else:
            pagination = SampleNature.query \
                .order_by(SampleNature.created_at.desc()).paginate(
                page, per_page=current_app.config['FLASK_PER_PAGE'],
                error_out=False)
    else:
        pagination = SampleNature.query \
            .order_by(SampleNature.created_at.desc()).paginate(
            page, per_page=current_app.config['FLASK_PER_PAGE'],
            error_out=False)
    list = pagination.items
    return render_template('sample_nature/list.html',
                           list=list, pagination=pagination,
                           title="type d'échantillon", search_form=search_form)


@bp.route('/sample_nature/add', methods=['GET', 'POST'])
@login_required
def add():
    add = True
    form = SampleNatureForm()
    if form.validate_on_submit():
        sample_nature = SampleNature(name=form.name.data,
                                 siggle=form.siggle.data,
                                 description=form.description.data,
                                 created_at=datetime.utcnow(),
                                 created_by=current_user.id)
        db.session.add(sample_nature)
        db.session.commit()
        flash(_('Data saved!'))
        return redirect(url_for('sample_nature.index'))
    return render_template('sample_nature/form.html', action="Add",
                           add=add, form=form,
                           title="Add sample_nature")


@bp.route('/sample_nature/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    add = False
    sample_nature = SampleNature.query.get_or_404(id)
    form = SampleNatureForm(obj=sample_nature)
    if form.validate_on_submit():
        sample_nature.name = form.name.data
        sample_nature.siggle = form.siggle.data
        sample_nature.description = form.description.data
        db.session.commit()
        flash('You have successfully edited the sample_nature.')

        # redirect to the bps page
        return redirect(url_for('sample_nature.index'))

    form.name.data = sample_nature.name
    form.siggle.data = sample_nature.siggle
    form.description.data = sample_nature.description
    return render_template('sample_nature/form.html', action="Edit",
                           add=add, form=form,
                           sample_nature=sample_nature, title="Edit sample_nature")


@bp.route('/sample_nature/<int:id>', methods=['GET', 'POST'])
@login_required
def detail(id):
    sample_nature = SampleNature.query.get_or_404(id)
    return render_template('sample_nature/detail.html', sample_nature=sample_nature)


@bp.route('/sample_nature/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    sample_nature = SampleNature.query.get_or_404(id)
    db.session.delete(sample_nature)
    db.session.commit()
    flash('You have successfully deleted the sample_nature.')

    # redirect to the bps page
    return redirect(url_for('sample_nature.index'))


@bp.route("/sample_nature/export", methods=['GET'])
@login_required
def export_data():
    return excel.make_response_from_tables(db.session, [SampleNature], "xls", file_name="export_data")


@bp.route("/sample_nature/import", methods=['GET', 'POST'])
@login_required
def import_data():
    if request.method == 'POST':
        def sample_nature_init_func(row):
            p = SampleNature(name=row['Nom'], siggle=row['Siggle'],
                           volume=row['Volume'], description=row['Description'])
            return p

        request.save_book_to_database(
            field_name='file', session=db.session,
            tables=[SampleNature],
            initializers=[sample_nature_init_func])
        return redirect(url_for('.handson_table'), code=302)
    return render_template('sample_nature/import.html')


@bp.route("/sample_nature/download", methods=['GET'])
@login_required
def download():
    query_sets = SampleNature.query.filter_by(id=1).all()
    column_names = ['name', 'siggle', 'desqcription']
    return excel.make_response_from_query_sets(query_sets, column_names, "xls", file_name="template")
