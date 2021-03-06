from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app.models import Basket

class SearchForm(FlaskForm):
    name = StringField(_l('Nom du panier'))
    submit = SubmitField('Search')

class BasketForm(FlaskForm):
    name = StringField(_l('Nom du panier'), validators=[DataRequired()])
    submit = SubmitField(_l('Enregistrer'))
