from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l


class StudyForm(FlaskForm):
    name = StringField(_l('Nom de l\'étude'), validators=[DataRequired()])
    description = TextAreaField(_l('Description'),
                             validators=[Length(min=0, max=255)])
    submit = SubmitField(_l('Enregistrer'))
