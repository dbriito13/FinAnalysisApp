from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from models.user import User
import re
import sys


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=5, max=50)])
    password = PasswordField(validators=[InputRequired(),
                                         Length(min=5, max=50)])
    submit = SubmitField('Create Account')

    def validate_username(self, username):
        '''
        Validate that the username does not already exist
        '''
        user = User.query.filter(User.username == username.data).first()
        if user is not None:
            raise ValidationError("Username already in use!")

    def validate_password(self, password):
        '''
        Simple password validation
        '''
        has_number = bool(re.search(r'\d', password.data))
        has_uppercase = bool(re.search(r'\w*[A-Z]\w*', password.data))
        if not has_number or not has_uppercase:
            raise ValidationError("Password must contain a number"
                                  " and uppercase letter")
