from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, FieldList, FormField
from wtforms import Form as NoCsrfForm
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app import db
from app.models import Sample


class SampleForm(FlaskForm):
    patient = SelectField(_l('Patient'), coerce=int, choices=[])
    code = StringField(_l('Code'), validators=[DataRequired()])
    sample_nature = SelectField(_l('Nature de prélèvement'), coerce=int, choices=[])
    sample_type = SelectField(_l('Type de prélèvement'), coerce=int, choices=[])
    date = StringField(_l('Date de prélèvement'), validators=[DataRequired()])
    site = StringField(_l('Site anatomique'), validators=[DataRequired()])
    jonc_type = SelectField(_l('Couleur de jonc'), coerce=int, choices=[])
    tube_type = SelectField(_l('Conditionement'), coerce=int, choices=[])
    mesure = SelectField(_l('Unité de mésure'), coerce=int, choices=[])
    volume = StringField(_l('Volume / Concentration'), validators=[DataRequired()])
    submit = SubmitField(_l('Enregistrer'))


class SearchForm(FlaskForm):
    code = StringField(_l('Code'), validators=[DataRequired()])
    sample_type = SelectField(_l('Nature du prélèvement'), coerce=int, choices=[])
    submit = SubmitField(_l('Recherche'))
