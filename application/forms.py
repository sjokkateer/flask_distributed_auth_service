from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired('Email is required'), Email('Valid email address required'), Length(min=3, max=254, message='Email must be at least %(min)d characters and at most %(max)d')])
    password = PasswordField('Password', validators=[DataRequired('Password is required'), Length(min=4, message='Password must be at least %(min)d characters')])
