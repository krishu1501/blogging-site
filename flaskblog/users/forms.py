from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from flaskblog.models import User
from datetime import date


class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=1,max=30)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=1,max=30)])
    username = StringField('Username',validators=[DataRequired(), Length(min=2,max=25)])
    email = StringField('Email',validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign up')

    def validate_username(self,username):
        user =  User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username is taken.Please choose another one.')
    
    def validate_email(self,email):
        user =  User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is taken.Please choose another one.')

class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=1,max=30)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=1,max=30)])
    username = StringField('Username',validators=[DataRequired(), Length(min=2,max=25)])
    email = StringField('Email',validators=[DataRequired(), Email()])
    gender = SelectField('Gender',choices=[('F','Female'),('M','Male'),('Oth','Others'),('Null','Prefer not to say'),])
    dob = DateField('Date of Birth',default=date.today)
    picture = FileField('Update Profile Picture',validators=[FileAllowed(['jpg','jpeg','png'])])
    submit = SubmitField('Update')

    def validate_username(self,username):
        if username.data!=current_user.username:
            user =  User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('This username is taken.Please choose another one.')
    
    def validate_email(self,email):
        if email.data!=current_user.email:
            user =  User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('This email is taken.Please choose another one.')


# to request reset of account password
class ResetRequestForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. Please register first.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Update Password')