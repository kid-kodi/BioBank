from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, SelectMultipleField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l


class AliquotForm(FlaskForm):
    support = SelectField(_l('Format de support'), coerce=int)
    samples = SelectMultipleField(_l('Liste des supports'), coerce=int)
    volume = StringField(_l('Volume / Quantité'), validators=[DataRequired()])
    mesure = SelectField(_l('Unité'), coerce=int)
    submit = SubmitField(_l('Enregistrer'))
