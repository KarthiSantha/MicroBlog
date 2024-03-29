from app import db
from flask import g,render_template,redirect,flash,url_for,request,jsonify
from app.auth.forms import LoginForm,RegistrationForm,ResetPasswordForm,ResetPasswordForm1
from flask_login import current_user,login_user,logout_user,login_required
from flask_babel import get_locale
from werkzeug.urls import url_parse
from app.models import User,Posts
from app.email import send_password_reset_email
from app.translate import translate
from datetime import datetime
from guess_language import guess_language
from app.auth import bp



@bp.before_request
def before_request():
	if current_user.is_authenticated:
		g.locale = str(get_locale())
		current_user.last_seen = datetime.utcnow()
		db.session.commit()


@bp.route('/login',methods = ['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('main.index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username = form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid Username or Password')
			return redirect(url_for('auth.login'))
		login_user(user,remember = form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('main.index')
		return redirect(next_page) 
		flash('Login requested by user {} is successful'.format(form.username.data))
		return redirect(url_for('main.index'))
	return render_template('login.html',tiitle = 'Sign In',form = form)

@bp.route('/register',methods = ['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('main.index'))
	form  = RegistrationForm()
	if form.validate_on_submit():
		user = User(username = form.username.data,email = form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congratulations you have registered')
		return redirect(url_for('auth.login'))
	return render_template('register.html',title = 'Register',form = form)


@bp.route('/reset_password_request',methods = ['GET','POST'])
def reset_password_request():
	if current_user.is_authenticated:
		return redirect(url_for('main.index'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data).first()
		if user is not None:
			send_password_reset_email(user)
		flash('Check your email for password reset link')
		return redirect(url_for('auth.login'))
	return render_template('reset_password_request.html',form=form)


@bp.route('/reset_password/<token>',methods = ['GET','POST'])
def reset_password(token):
	if current_user.is_authenticated:
		return redirect(url_for('main.index'))
	user = User.verify_reset_password_token(token)
	if not user:
		print('hi')
		return redirect(url_for('main.index'))
	form = ResetPasswordForm1()
	if form.validate_on_submit():
		user.set_password(form.password.data)
		db.session.commit()
		flash('Your Password is reset')
		return redirect(url_for('auth.login'))
	return render_template('reset_password.html',form = form)

@bp.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('main.index'))