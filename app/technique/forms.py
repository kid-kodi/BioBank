from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l


class TechniqueForm(FlaskForm):
    category = SelectField(_l('Catégorie'), coerce=int, choices=[(1, "Pushing"), (2, "Pulling")])
    name = StringField(_l('Nom de la technique'), validators=[DataRequired()])
    in_number = StringField(_l('Nombre d\'échantillon utilisé'), validators=[DataRequired()])
    out_number = StringField(_l('Nombre d\'échantillon sortant'), validators=[DataRequired()])
    description = TextAreaField(_l('Description'),
                             validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Enregistrer'))
