from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import BooleanField, StringField, PasswordField, SubmitField, TextAreaField, ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flaskblog.models  import User

class RegistrationForm(FlaskForm):
    """form used by users to register"""
    username = StringField('Username', validators=[DataRequired(), 
                                                    Length(min=2, max=60)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm password', validators=[DataRequired(),
                                                                    EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        """checks if the user  name is already in use"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That usename already exists. Please choose another one')

    def validate_email(self, email):
        """checks if the username is already in use"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email already exists. Try logging in, or using another email')

class LoginForm(FlaskForm):
    """login form for the user to log in after registration"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')
    
class UpdateAccountForm(FlaskForm):
    """form used by users to register"""
    username = StringField('Username', validators=[DataRequired(), 
                                                    Length(min=2, max=60)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update profile picture', validators=[FileAllowed(['jpg', 'png', 'img'])])
    submit = SubmitField('Update')
    
    def validate_username(self, username):
        """checks if the user  name is already in use"""
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That usename already exists. Please choose another one')

    def validate_email(self, email):
        """checks if the username is already in use"""
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email already exists. Try logging in, or using another email')
            
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators= [DataRequired()])
    submit = SubmitField('Post')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    def validate_email(self, email):
        """checks if the username is already in use"""
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('No account with that email please register')
    submit = SubmitField('Request Password Reset')
    
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm password', validators=[DataRequired(),
                                                                    EqualTo('password')])
    submit = SubmitField('Reset Pasword')
    