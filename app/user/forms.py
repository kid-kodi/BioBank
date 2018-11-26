# app/departement/user.py

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo


class UserForm(FlaskForm):
    """
    Form for departement to add or edit a user
    """
    email = StringField('Adresse email', validators=[DataRequired(), Email()])
    username = StringField('Pseudonyme', validators=[DataRequired()])
    first_name = StringField('Nom', validators=[DataRequired()])
    last_name = StringField('Prénoms', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[
        DataRequired(),
        EqualTo('confirm_password')
    ])
    confirm_password = PasswordField('Confirmer le mot de passe')
    submit = SubmitField('Enregistrer')
