from app import app,db
from flask import g,render_template,redirect,flash,url_for,request,jsonify
from app.forms import LoginForm,RegistrationForm,EditProfileForm,PostForm,ResetPasswordForm,ResetPasswordForm1
from flask_login import current_user,login_user,logout_user,login_required
from flask_babel import get_locale
from werkzeug.urls import url_parse
from app.models import User,Posts
from app.email import send_password_reset_email
from app.translate import translate
from datetime import datetime
from guess_language import guess_language


@app.before_request
def before_request():
	if current_user.is_authenticated:
		g.locale = str(get_locale())
		current_user.last_seen = datetime.utcnow()
		db.session.commit()

@app.route('/',methods = ['GET','POST'])
@app.route('/index',methods = ['GET','POST'])
@login_required
def index():#1
	form = PostForm()
	if form.validate_on_submit():
		language = guess_language(form.post.data)
		if language == 'UNKNOWN' or len(language)>6:
			language = ''
		post = Posts(body=form.post.data,language = language,author=current_user)
		db.session.add(post)
		db.session.commit()
		flash('Your Post is Live !')
		return redirect(url_for('index'))
	page = request.args.get('page',1,type = int)
	posts = current_user.followed_posts().paginate(
		page,app.config['POSTS_PER_PAGE'],False)
	next_url = url_for('explore', page=posts.next_num) if posts.has_next else None
	prev_url = url_for('explore', page=posts.prev_num) if posts.has_prev else None
	return render_template('index.html',title = 'Machine Learning',user = user,form = form,posts = posts.items,next_url = next_url,prev_url = prev_url)

@app.route('/explore')
@login_required
def explore():#2
	page = request.args.get('page',1,type = int)
	posts = Posts.query.order_by(Posts.timestamp.desc()).paginate(
		page,app.config['POSTS_PER_PAGE'],False)
	next_url = url_for('explore', page=posts.next_num) if posts.has_next else None
	prev_url = url_for('explore', page=posts.prev_num) if posts.has_prev else None
	return render_template('index.html',title = 'Explore',
		posts=posts.items,next_url = next_url,prev_url = prev_url)

@app.route('/login',methods = ['GET','POST'])
def login():#3
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username = form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid Username or Password')
			return redirect(url_for('login'))
		login_user(user,remember = form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(next_page) 
		flash('Login requested by user {} is successful'.format(form.username.data))
		return redirect(url_for('index'))
	return render_template('login.html',tiitle = 'Sign In',form = form)

@app.route('/register',methods = ['GET','POST'])
def register():#4
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form  = RegistrationForm()
	if form.validate_on_submit():
		user = User(username = form.username.data,email = form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congratulations you have registered')
		return redirect(url_for('login'))
	return render_template('register.html',title = 'Register',form = form)

@app.route('/edit_profile',methods = ['GET','POST'])
def edit_profile():#5
	form = EditProfileForm(current_user.username)
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.about_me =form.about_me.data
		db.session.commit()
		flash('Your changes are saved')
		return redirect(url_for('edit_profile'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.about_me.data = current_user.about_me
	return render_template('edit_profile.html',title = 'Edit Profile',form=form)

@app.route('/follow/<username>')
@login_required
def follow(username):#6
	user = User.query.filter_by(username = username).first()
	if user is None:
		flash('User {} not found'.format(username))
		return redirect(url_for('index'))
	if user == current_user:
		flash('You cannot follow yourself')
		return redirect(url_for('user',username = username))
	current_user.follow(user)
	db.session.commit()
	flash('You are following {}!'.format(username))
	return redirect(url_for('user',username = username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):#7
	user = User.query.filter_by(username = username).first()
	if user is None:
		flash('User {} not found'.format(username))
		return redirect(url_for('index'))
	if user == current_user:
		flash('You cannot unfollow yourself')
		return redirect(url_for('user',username = username))
	current_user.unfollow(user)
	db.session.commit()
	flash('You are following {}!'.format(username))
	return redirect(url_for('user',username = username))

@app.route('/reset_password_request',methods = ['GET','POST'])
def reset_password_request():#8
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data).first()
		if user is not None:
			send_password_reset_email(user)
		flash('Check your email for password reset link')
		return redirect(url_for('login'))
	return render_template('reset_password_request.html',form=form)


@app.route('/reset_password/<token>',methods = ['GET','POST'])
def reset_password(token):#9
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	user = User.verify_reset_password_token(token)
	if not user:
		print('hi')
		return redirect(url_for('index'))
	form = ResetPasswordForm1()
	if form.validate_on_submit():
		user.set_password(form.password.data)
		db.session.commit()
		flash('Your Password is reset')
		return redirect(url_for('login'))
	return render_template('reset_password.html',form = form)



@app.route('/user/<username>')
@login_required
def user(username):#10
	user = User.query.filter_by(username =username).first_or_404()
	page = request.args.get('page',1,type = int)
	posts = user.posts.order_by(Posts.timestamp.desc()).paginate(
		page,app.config['POSTS_PER_PAGE'],False)
	next_url = url_for('user',username = user.username,page = posts.next_num) if posts.has_next else None
	prev_url = url_for('user',username = user.username,page = posts.prev_num) if posts.has_prev else None
	return render_template('user.html',user=user,
		posts=posts.items,next_url = next_url,prev_url= prev_url)


@app.route('/translate', methods=['POST'])
@login_required
def translate_text():#11
	return jsonify({'text': 
		translate(
			request.form['text'],
			request.form['source_language'],
			request.form['dest_language'])})


@app.route('/logout')
def logout():#12
	logout_user()
	return redirect(url_for('index'))