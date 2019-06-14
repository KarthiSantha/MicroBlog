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


class EditProfileForm(FlaskForm):

	def __init__(self,original_username):
		super(EditProfileForm, self).__init__()
		self.original_username = current_user.username
			
	#self.original_username = current_user.username
	username = StringField('Username',validators = [DataRequired()])
	about_me = TextAreaField('About Me',validators = [Length(min = 0,max =140)])
	submit = SubmitField('Submit')

	def validate_username(self,username):
		if username.data != self.original_username:
			user = User.query.filter_by(username = username.data).first()
			if user is not None:
				return ValidationError('Please Use a different Username')
		flash('Username already exists')

class ResetPasswordForm(FlaskForm):
	email = StringField('Email',validators = [DataRequired(),Email()])
	submit = SubmitField('Request Password')


class ResetPasswordForm1(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

class PostForm(FlaskForm):
	post = TextAreaField('Say something',validators = [DataRequired(),Length(min = 1,max = 140)])
	submit = SubmitField('submit')