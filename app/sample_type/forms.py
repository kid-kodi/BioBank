from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app.models import SampleType


class SearchForm(FlaskForm):
    name = StringField(_l('Modèle'))
    submit = SubmitField('Search')


class SampleTypeForm(FlaskForm):
    name = StringField(_l('Nom du modèle'), validators=[DataRequired()])
    volume = StringField(_l('Volume'), validators=[DataRequired()])
    siggle = StringField(_l('Abbreviation'))
    description = TextAreaField(_l('Volume'), validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Enregistrer'))
