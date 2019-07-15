from flask_login import current_user
from flask_wtf import FlaskForm
from flask import flash
from wtforms import StringField, PasswordField, BooleanField, SubmitField,TextAreaField
from wtforms.validators import DataRequired,Email,EqualTo,ValidationError,Length
from app.models import User


class LoginForm(FlaskForm):
	username = StringField('Username',validators = [DataRequired()]) 
	password = PasswordField('Password',validators = [DataRequired()])
	remember_me = BooleanField('Remember me')
	submit = SubmitField('Sign In')
	
class RegistrationForm(FlaskForm):
	username = StringField('Username',validators = [DataRequired()])
	email = StringField('Email',validators = [DataRequired(),Email()])
	password = PasswordField('Password',validators = [DataRequired()])
	repeat_password = PasswordField('Repeat Password',validators = [DataRequired(),EqualTo('password')])
	submit = SubmitField('Register')

	def validate_username(self,username):
		user = User.query.filter_by(username = username.data).first()
		if user is not None:
			return ValidationError('Please Use a different Username')

	def validate_email(self,email):
		user = User.query.filter_by(email = email.data).first()
		if user is not None:
			return ValidationError('Please Use a different Email ID')


class ResetPasswordForm(FlaskForm):
	email = StringField('Email',validators = [DataRequired(),Email()])
	submit = SubmitField('Request Password')


class ResetPasswordForm1(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')
