from flask import render_template, request, redirect, url_for
from app import db
from app.models import Customer, Box, Rack, Equipment, Hole, Basket, Sample
from app.setup import bp


@bp.route('/setup')
def index():
    return render_template('setup/index.html')


@bp.route("/import", methods=['GET', 'POST'])
def doimport():
    if request.method == 'POST':

        def category_init_func(row):
            c = Customer(row['display_as'])
            c.id = row['id']
            return c


        request.save_book_to_database(
            field_name='file', session=db.session,
            tables=[Customer],
            initializers=[category_init_func])
        return redirect(url_for('.handson_table'), code=302)
    return '''
    <!doctype html>
    <title>Upload an excel file</title>
    <h1>Excel file upload (xls, xlsx, ods please)</h1>
    <form action="" method=post enctype=multipart/form-data><p>
    <input type=file name=file><input type=submit value=Upload>
    </form>
    '''


@bp.route('/export', methods=['GET', 'POST'])
def doexport():
    return render_template('setup/backup.html')
