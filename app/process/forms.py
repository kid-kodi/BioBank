from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l


class ProcessForm(FlaskForm):
    sample = SelectField(_l('Choisir un échantillon'), coerce=int)
    number = StringField(_l('Nombre d\'aliquots'), validators=[DataRequired()])
    submit = SubmitField(_l('Enregistrer'))
