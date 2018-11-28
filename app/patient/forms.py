from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, FieldList, FormField
from wtforms import Form as NoCsrfForm
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l


from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, FieldList, FormField
from wtforms import Form as NoCsrfForm
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app import db
from app.models import Sample


class ModelFieldList(FieldList):
    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop("model", None)
        super(ModelFieldList, self).__init__(*args, **kwargs)
        if not self.model:
            raise ValueError("ModelFieldList requires model to be set")

    def populate_obj(self, obj, name):
        while len(getattr(obj, name)) < len(self.entries):
            newModel = self.model()
            db.session.add(newModel)
            getattr(obj, name).append(newModel)
        while len(getattr(obj, name)) > len(self.entries):
            db.session.delete(getattr(obj, name).pop())
        super(ModelFieldList, self).populate_obj(obj, name)


class SampleForm(NoCsrfForm):
    code = StringField(_l('Code'))
    date = StringField(_l('Date de prélèvement'))
    technique = StringField(_l('Technique de préparation'))
    sample_nature = SelectField(_l('Nature de prélèvement'), coerce=int, choices=[])
    sample_type = SelectField(_l('Type de prélèvement'), coerce=int, choices=[])
    number = StringField(_l('Nombre de tube'), validators=[DataRequired()])
    site = StringField(_l('Site anatomique'))
    tube_type = SelectField(_l('Conditionement'), coerce=int, choices=[])
    jonc_type = SelectField(_l('Type de jonc'), coerce=int, choices=[])
    mesure = SelectField(_l('Unité de mésure'), coerce=int, choices=[])
    volume = StringField(_l('Volume / Concentration'), validators=[DataRequired()])
    results = TextAreaField(_l('Résultat des examens'))


class PatientForm(FlaskForm):
    code = StringField(_l('Code Patient'))
    order = SelectField(_l('Selectionner un numéro de commande'), coerce=int, choices=[])
    sexe = SelectField(_l('Sexe'), coerce=int, choices=[(1, 'Male'), (2, 'Femelle')])
    birthday = StringField(_l('Date de naissaince'))
    city = StringField(_l('Lieu d\'habitation'))
    job = StringField(_l('Fonction'))
    age = StringField(_l('Age'))
    clinical_data = TextAreaField(_l('Renseignement clinique'))
    samples = ModelFieldList(FormField(SampleForm), min_entries=1, model=Sample)
    submit = SubmitField(_l('Enregistrer'))


class SearchForm(FlaskForm):
    code = StringField(_l('Code patient'), validators=[DataRequired()])
    submit = SubmitField(_l('Recherche'))