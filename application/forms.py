from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired('Email is required'), Email('Valid email address required'), Length(min=3, max=254, message='Email must be at least %(min)d characters and at most %(max)d')])
    password = PasswordField('Password', validators=[DataRequired('Password is required'), Length(min=4, message='Password must be at least %(min)d characters')])


class ImageForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired('Title is required'), Length(min=1, max=254, message='Title must be at least %(min)d characters and at most %(max)d')])
    image = FileField('Image', validators=[FileRequired('Image is required'), FileAllowed(['jpg', 'png', 'gif'], 'Images and gifs only!')])
