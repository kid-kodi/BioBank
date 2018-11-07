from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l


class ProjectForm(FlaskForm):
    customer = SelectField(_l('Client'), coerce=int)
    study = SelectField(_l('Etude'), coerce=int)
    subject = SelectField(_l('Thématique'), coerce=int)
    program = SelectField(_l('Programme'), coerce=int)
    title = StringField(_l('Titre'), validators=[DataRequired()])
    description = TextAreaField(_l('Description'),
                                validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Enregistrer'))


class OrderForm(FlaskForm):
    customer = SelectField(_l('Client'), coerce=int, choices=[])
    study = SelectField(_l('Etude'), coerce=int, choices=[])
    subject = SelectField(_l('Thématique'), coerce=int, choices=[])
    program = SelectField(_l('Programme'), coerce=int, choices=[])
    author = StringField(_l('Preleveur ID'), validators=[DataRequired()])

    transport_date = StringField(_l('Date de transport'), validators=[DataRequired()])
    temperature_date = StringField(_l('Temperature de transport'), validators=[DataRequired()])
    code = StringField(_l('Code Patient'), validators=[DataRequired()])
    birthday = StringField(_l('Date de naissaince'), validators=[DataRequired()])
    origin = SelectField(_l('Règne'), coerce=int, choices=[])
    sampleType = SelectField(_l('Nature de prélèvement'), coerce=int, choices=[])
    date = StringField(_l('Date de prélèvement'), validators=[DataRequired()])
    site = StringField(_l('Site anatomique'), validators=[DataRequired()])
    tubeType = SelectField(_l('Conditionement'), coerce=int, choices=[])
    volume = StringField(_l('Volume'), validators=[DataRequired()])

    submit = SubmitField(_l('Enregistrer'))


class SampleForm(FlaskForm):
    customer = SelectField(_l('Client'), coerce=int, choices=[])
    study = SelectField(_l('Etude'), coerce=int, choices=[])
    subject = SelectField(_l('Thématique'), coerce=int, choices=[])
    program = SelectField(_l('Programme'), coerce=int, choices=[])
    author = StringField(_l('Preleveur ID'), validators=[DataRequired()])

    transport_date = StringField(_l('Date de transport'), validators=[DataRequired()])
    temperature_date = StringField(_l('Temperature de transport'), validators=[DataRequired()])
    code = StringField(_l('Code Patient'), validators=[DataRequired()])
    birthday = StringField(_l('Date de naissaince'), validators=[DataRequired()])
    origin = SelectField(_l('Règne'), coerce=int, choices=[])
    sampleType = SelectField(_l('Nature de prélèvement'), coerce=int, choices=[])
    date = StringField(_l('Date de prélèvement'), validators=[DataRequired()])
    site = StringField(_l('Site anatomique'), validators=[DataRequired()])
    tubeType = SelectField(_l('Conditionement'), coerce=int, choices=[])
    volume = StringField(_l('Volume'), validators=[DataRequired()])

    submit = SubmitField(_l('Enregistrer'))
