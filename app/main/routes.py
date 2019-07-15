from app import db
from flask import current_app,g,render_template,redirect,flash,url_for,request,jsonify
from app.main.forms import EditProfileForm,PostForm
from flask_login import current_user,login_user,logout_user,login_required
from flask_babel import get_locale
from werkzeug.urls import url_parse
from app.models import User,Posts
from app.email import send_password_reset_email
from app.translate import translate
from datetime import datetime
from guess_language import guess_language
from app.main import bp


@bp.route('/',methods = ['GET','POST'])
@bp.route('/index',methods = ['GET','POST'])
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
		return redirect(url_for('main.index'))
	page = request.args.get('page',1,type = int)
	posts = current_user.followed_posts().paginate(
		page,current_app.config['POSTS_PER_PAGE'],False)
	next_url = url_for('main.explore', page=posts.next_num) if posts.has_next else None
	prev_url = url_for('main.explore', page=posts.prev_num) if posts.has_prev else None
	return render_template('index.html',title = 'Machine Learning',user = user,form = form,posts = posts.items,next_url = next_url,prev_url = prev_url)


@bp.route('/explore')
@login_required
def explore():#2
	page = request.args.get('page',1,type = int)
	posts = Posts.query.order_by(Posts.timestamp.desc()).paginate(
		page,current_app.config['POSTS_PER_PAGE'],False)
	next_url = url_for('explore', page=posts.next_num) if posts.has_next else None
	prev_url = url_for('explore', page=posts.prev_num) if posts.has_prev else None
	return render_template('index.html',title = 'Explore',
		posts=posts.items,next_url = next_url,prev_url = prev_url)


@bp.route('/edit_profile',methods = ['GET','POST'])
def edit_profile():#5
	form = EditProfileForm(current_user.username)
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.about_me =form.about_me.data
		db.session.commit()
		flash('Your changes are saved')
		return redirect(url_for('main.edit_profile'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.about_me.data = current_user.about_me
	return render_template('edit_profile.html',title = 'Edit Profile',form=form)


@bp.route('/follow/<username>')
@login_required
def follow(username):#6
	user = User.query.filter_by(username = username).first()
	if user is None:
		flash('User {} not found'.format(username))
		return redirect(url_for('main.index'))
	if user == current_user:
		flash('You cannot follow yourself')
		return redirect(url_for('main.user',username = username))
	current_user.follow(user)
	db.session.commit()
	flash('You are following {}!'.format(username))
	return redirect(url_for('main.user',username = username))

@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):#7
	user = User.query.filter_by(username = username).first()
	if user is None:
		flash('User {} not found'.format(username))
		return redirect(url_for('main.index'))
	if user == current_user:
		flash('You cannot unfollow yourself')
		return redirect(url_for('main.user',username = username))
	current_user.unfollow(user)
	db.session.commit()
	flash('You are following {}!'.format(username))
	return redirect(url_for('main.user',username = username))

@bp.route('/user/<username>')
@login_required
def user(username):#10
	user = User.query.filter_by(username =username).first_or_404()
	page = request.args.get('page',1,type = int)
	posts = user.posts.order_by(Posts.timestamp.desc()).paginate(
		page,current_app.config['POSTS_PER_PAGE'],False)
	next_url = url_for('main.user',username = user.username,page = posts.next_num) if posts.has_next else None
	prev_url = url_for('main.user',username = user.username,page = posts.prev_num) if posts.has_prev else None
	return render_template('user.html',user=user,
		posts=posts.items,next_url = next_url,prev_url= prev_url)


@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():#11
	return jsonify({'text': 
		translate(
			request.form['text'],
			request.form['source_language'],
			request.form['dest_language'])})