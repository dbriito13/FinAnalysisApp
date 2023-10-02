from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from user import User


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=5, max=50)])
    password = PasswordField(validators=[InputRequired(),
                                         Length(min=5, max=50)])
    submit = SubmitField('Login')

    def validate_username(self, username):
        '''
        Validate that the username exists
        '''
        user = User.query.filter(User.username == username.data).first()
        if user is None:
            raise ValidationError("Username does not exist!")
