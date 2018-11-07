from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, FieldList, FormField
from wtforms import Form as NoCsrfForm
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l


class PatientForm(FlaskForm):

    origin = SelectField(_l('Règne'), coerce=int, choices=[])
    code = StringField(_l('Code Patient'), validators=[DataRequired()])
    sexe = SelectField(_l('Sexe'), choices=[(1, 'Male'), (2, 'Femelle')])
    birthday = StringField(_l('Date de naissaince'), validators=[DataRequired()])
    submit = SubmitField(_l('Enregistrer'))
