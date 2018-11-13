from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, FieldList, FormField, RadioField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import Form as NoCsrfForm
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app import db
from app.models import Sample



class OrderForm(FlaskForm):
    customer = SelectField(_l('Client'), coerce=int, choices=[])
    project = SelectField(_l('Projet'), coerce=int, choices=[])
    firstname = StringField(_l('Nom du deposant'), validators=[DataRequired()])
    lastname = StringField(_l('Prénoms du deposant'), validators=[DataRequired()])
    telephone = StringField(_l('Téléphone'), validators=[DataRequired()])
    transport_date = StringField(_l('Date de transport'), validators=[DataRequired()])
    temperature = SelectField(_l('Température'), coerce=int, choices=[])
    submit = SubmitField(_l('Suivant'))
