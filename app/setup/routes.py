from flask import render_template, request, redirect, url_for, flash
import flask_excel as excel
from flask_login import current_user, login_required
from app import db
from app.models import User, Category, Customer, Project, Order, Study, Subject, Program, Origin, Mesure, JoncType, \
    Patient, Support, SampleNature, SampleType, Temperature, Box, Rack, Equipment, Hole, Sample, Basket, EquipmentType, \
    BoxType, Room
from app.setup import bp
from flask_babel import _


@bp.route('/setup')
@login_required
def index():
    return render_template('setup/index.html')


@bp.route("/import", methods=['GET', 'POST'])
@login_required
def doimport():
    if request.method == 'POST':

        def category_init(row):
            category = Category()
            num = Category.query.filter_by(name=row['Nom']).count()
            if num > 0:
                Category.query.delete()
            category.name = row['Nom']
            category.description = row['Description']
            return category

        def study_init(row):
            study = Study()
            num = Study.query.filter_by(name=row['Nom']).count()
            if num > 0:
                Study.query.delete()
            study.name = row['Nom']
            study.description = row['Description']
            return study

        def subject_init(row):
            subject = Subject()
            num = Subject.query.filter_by(name=row['Nom']).count()
            if num > 0:
                Subject.query.delete()
            study = Study.query.filter_by(name=row['Etude']).first()
            subject.name = row['Nom']
            subject.description = row['Description']
            subject.study = study
            return subject

        def program_init(row):
            program = Program()
            num = Program.query.filter_by(name=row['Nom']).count()
            if num > 0:
                Program.query.delete()
            subject = Subject.query.filter_by(name=row['Thematique']).first()
            program.name = row['Nom']
            program.description = row['Description']
            program.subject = subject
            return program

        def origin_init(row):
            origin = Origin()
            num = Origin.query.filter_by(name=row['Nom']).count()
            if num > 0:
                Origin.query.delete()
            origin.name = row['Nom']
            origin.siggle = row['Siggle']
            origin.description = row['Description']
            return origin

        def sample_nature_init(row):
            sample_nature = SampleNature()
            num = SampleNature.query.filter_by(name=row['Nom']).count()
            if num > 0:
                SampleNature.query.delete()
            sample_nature.name = row['Nom']
            sample_nature.siggle = row['Siggle']
            sample_nature.description = row['Description']
            return sample_nature

        def sample_type_init(row):
            sample_type = SampleType()
            num = SampleType.query.filter_by(name=row['Nom']).count()
            if num > 0:
                SampleType.query.delete()
            sample_type.name = row['Nom']
            sample_type.siggle = row['Siggle']
            sample_type.description = row['Description']
            return sample_type

        def mesure_init(row):
            mesure = Mesure()
            num = Mesure.query.filter_by(name=row['Nom']).count()
            if num > 0:
                Mesure.query.delete()
            mesure.name = row['Nom']
            mesure.siggle = row['Siggle']
            mesure.description = row['Description']
            return mesure

        def jonc_type_init(row):
            jonc_type = JoncType()
            num = JoncType.query.filter_by(name=row['Nom']).count()
            if num > 0:
                JoncType.query.delete()
            jonc_type.name = row['Nom']
            jonc_type.siggle = row['Siggle']
            jonc_type.description = row['Description']
            return jonc_type

        def support_init(row):
            support = Support()
            num = Support.query.filter_by(name=row['Nom']).count()
            if num > 0:
                Support.query.delete()
            support.name = row['Nom']
            support.volume = row['Volume']
            support.siggle = row['Siggle']
            support.description = row['Description']
            return support

        def temperature_init(row):
            temperature = Temperature()
            num = Temperature.query.filter_by(name=row['Nom']).count()
            if num > 0:
                Temperature.query.delete()
            temperature.id = row['Id']
            temperature.name = row['Nom']
            return temperature

        def equipment_type_init(row):
            equipment_type = EquipmentType()
            num = EquipmentType.query.filter_by(name=row['Nom']).count()
            if num > 0:
                EquipmentType.query.delete()
            equipment_type.name = row['Nom']
            equipment_type.description = row['Description']
            return equipment_type

        def box_type_init(row):
            box_type = BoxType()
            num = BoxType.query.filter_by(name=row['Nom']).count()
            if num > 0:
                BoxType.query.delete()
            box_type.name = row['Nom']
            box_type.max_number = row['Espace total']
            box_type.description = row['Description']
            return box_type

        def room_init(row):
            room = Room()
            num = Room.query.filter_by(name=row['Nom']).count()
            if num > 0:
                Room.query.delete()
            room.name = row['Nom']
            room.max_number = row['Espace total']
            room.description = row['Description']
            return room

        def equipment_init(row):
            equipment = Equipment()
            num = Equipment.query.filter_by(name=row['Nom']).count()
            if num > 0:
                Equipment.query.delete()
            room = Room.query.filter_by(name=row['Salle']).first()
            equipment_type = EquipmentType.query.filter_by(name=row['Type Equipement']).first()
            equipment.room = room
            equipment.equipment_type = equipment_type
            equipment.name = row['Nom']
            equipment.horizontal = row['Horizontale']
            equipment.vertical = row['Verticale']
            equipment.status = 0
            print(row['Nom'])
            equipment.max_number = int(equipment.horizontal) * int(equipment.vertical)
            equipment.description = row['Description']
            return equipment

        def rack_init(row):
            rack = Rack()
            num = Rack.query.filter_by(name=row['Nom']).count()
            if num > 0:
                Rack.query.delete()
            equipment = Equipment.query.filter_by(name=row['Equipement']).first()
            rack.equipment = equipment
            rack.name = row['Nom']
            rack.horizontal = row['Horizontale']
            rack.vertical = row['Verticale']
            rack.status = 0
            rack.max_number = int(rack.horizontal) * int(rack.vertical)
            rack.description = row['Description']
            return rack

        def box_init(row):
            box = Box()
            num = Box.query.filter_by(name=row['Nom']).count()
            if num > 0:
                Box.query.delete()
            rack = Rack.query.filter_by(name=row['Rack']).first()
            box_type = BoxType.query.filter_by(name=row['Type Boite']).first()
            box.box_type = box_type
            box.rack = rack
            box.name = row['Nom']
            box.horizontal = row['Horizontale']
            box.vertical = row['Verticale']
            box.status = 0
            box.max_number = int(box.horizontal) * int(box.vertical)
            box.description = row['Description']
            return rack

        def customer_init(row):
            category = Category.query.filter_by(name=row['Categorie']).first()
            customer = Customer()
            customer.id = row['Id']
            customer.category = category
            customer.display_as = row['Raison Sociale']
            customer.firstname = row['Nom']
            customer.lastname = row['Prénoms']
            customer.adresse = row['Adresse']
            customer.telephone = row['Téléphone']
            customer.email = row['Email']
            return customer

        def project_init(row):
            c = Project.query.filter_by(name=row['Categorie']).first()
            customer = Customer()
            customer.id = row['Id']
            customer.category = c
            customer.display_as = row['Raison Sociale']
            customer.firstname = row['Nom']
            customer.lastname = row['Prénoms']
            customer.adresse = row['Adresse']
            customer.telephone = row['Téléphone']
            customer.email = row['Email']
            return customer

        request.save_book_to_database(
            field_name='file', session=db.session,
            tables=[Category, Study, Subject, Program, Origin, SampleNature, SampleType, Mesure, JoncType,
                    Support, Temperature, EquipmentType, BoxType, Room, Equipment, Rack, Box],
            initializers=[category_init, study_init, subject_init, program_init, origin_init,
                          sample_nature_init, sample_type_init, mesure_init, jonc_type_init, support_init,
                          temperature_init, equipment_type_init, box_type_init, room_init, equipment_init,
                          rack_init, box_init])
        flash(_('Initialisation terminé avec succèss.'))
        return redirect(url_for('main.index'))
    return render_template('setup/import.html')


@bp.route("/handson_view", methods=['GET'])
@login_required
def handson_table():
    return excel.make_response_from_tables(
        db.session, [User, Category, Study, Subject, Program, Origin, SampleNature, SampleType, Mesure, JoncType,
                     Support, Temperature, Basket], 'setup/handsontable.html')


@bp.route("/export", methods=['GET'])
@login_required
def doexport():
    return excel.make_response_from_tables(db.session,
                                           [User, Category, Customer, Project, Order, Study, Subject, Program, Origin,
                                            Mesure, JoncType, Patient, Support, Sample, SampleNature, SampleType,
                                            Temperature, Box, Rack, Equipment, Hole, Sample], "xls",
                                           file_name="template")
