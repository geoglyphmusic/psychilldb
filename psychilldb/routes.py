from flask import request, flash, url_for, render_template, redirect, request, abort
from psychilldb import app, db, bcrypt, mail
from psychilldb.models import Track, User
from psychilldb.forms import (TrackForm, SearchForm, UploadForm, RegistrationForm, LoginForm, UpdateAccountForm, UpdatePasswordForm,
		RequestResetForm, ResetPasswordForm)
from psychilldb.algorithms import similarity, KeyCycle
from pyexcel_ods3 import get_data
from operator import itemgetter
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message


@app.route('/')
@app.route('/home')
def home():
	return render_template('home.html', nav=True)


@app.route('/about')
def about():
    return render_template('about.html', title='About', nav=True)

def send_registration_email(user):
	msg = Message('Account Created',
				sender='psychilldb@gmail.com',
				recipients=[user.email])
	msg.body = f'''Thanks for making an account with PsyChillDB. If you have any questions, feel free to email me at geoglyphmusic@gmail.com. You can login here: geoglyph.pythonanywhere.com/login.
G
	'''
	mail.send(msg)

@app.route("/register", methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, email=form.email.data, password=hashed_password)
		db.session.add(user)
		db.session.commit()
		send_registration_email(user)
		flash(f'Account created for {form.username.data}. An email has been sent to the address given.', 'success')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form, nav=True)


@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')# Redirects user to the page they were trying to access before logging in
			return redirect(next_page) if next_page else redirect(url_for('home'))
		else:
			flash('Login unsuccessful. Please try again.', 'danger')
	return render_template('login.html', title='Login', form=form, nav=True)


@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('home'))


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
	return render_template('account.html', title='Account', nav=True)


@app.route('/updateaccount', methods=['GET', 'POST'])
@login_required
def updateaccount():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		current_user.username=form.username.data
		current_user.email=form.email.data
		db.session.commit()
		flash('Your account has been updated.', 'success')
		return redirect(url_for('account'))
	elif request.method == "GET":# Populates the update form with the current user's data
		form.username.data = current_user.username
		form.email.data = current_user.email
	return render_template('updateaccount.html', title='Update Account', form=form, nav=True)


@app.route('/updatepassword', methods=['GET', 'POST'])
def updatepassword():
	form = UpdatePasswordForm()
	if form.validate_on_submit():
		if bcrypt.check_password_hash(current_user.password, form.old_password.data):
			hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
			current_user.password = hashed_password
			db.session.commit()
			flash('Your account has been updated.', 'success')
			return redirect(url_for('account'))
		else:
			flash('The previous password is incorrect. Please try again.', 'danger')
	return render_template('updatepassword.html', title='Update Password', form=form, nav=True)


@app.route('/contribute', methods=['GET', 'POST'])
@login_required
def contribute():
	form = TrackForm()
	if form.validate_on_submit():
		if Track.query.filter_by(artist=form.artist.data, album=form.album.data, title=form.title.data).first():# Checks whether item is already in the database
			flash(form.artist.data + ' - ' + form.title.data + ' is already in the database.', 'danger')
		else:
			new_track = Track(artist=form.artist.data, album=form.album.data, title=form.title.data,
				year=form.year.data, tempo=form.tempo.data, key=form.key.data + ' ' + form.mode.data,
				energy=form.energy.data, contributor=current_user)
			db.session.add(new_track)
			db.session.commit()
			flash(new_track.artist + ' - ' + new_track.title + ' - uploaded.', 'success')
	return render_template('contribute.html', title='Contribute', form=form, nav=True)


@app.route('/batchupload', methods=['GET', 'POST'])
@login_required
def batchupload():
	form = UploadForm()
	if form.validate_on_submit():
		file = form.file.data
		Data = get_data(file, start_row=1, start_column=0)
		ActiveData = Data['Sheet1']
		for item in ActiveData:
			if len(item)==0:#Checks for blank rows, especially at the end of the list, in order to avoid 'out of range' errors
				continue# Skips the current item
			elif len(item)<7:
				flash(item[0] + ' is missing some information.', 'danger')
				continue
			elif item[5] not in KeyCycle.keys():#Checks whether the key information is consistent with the database key system
				flash(item[0] + ' - ' + item[2] + ' does not have a recognised key.', 'danger')
			elif item[6] not in (1, 2, 3, 4, 5):
				flash(str(item[0]) + ' - ' + str(item[2]) + ' does not have a recognised energy value.', 'danger')
			elif Track.query.filter_by(artist=item[0], album=item[1], title=item[2]).first():# Checks whether item is already in the database
				flash(str(item[0]) + ' - ' + str(item[2]) + ' is already in the database.', 'danger')
			else:
				track = Track(artist=str(item[0]), album=str(item[1]), title=str(item[2]), year=item[3], tempo=item[4],
							key=item[5], energy=item[6], contributor=current_user)
				if track.tempo >= 130:
					track.tempo = track.tempo/2
				db.session.add(track)
				flash(str(item[0]) + ' - ' + str(item[2]) + ' - uploaded.', 'success')
		db.session.commit()
		return redirect(url_for('batchupload'))
	return render_template('batchupload.html', title='Batch Upload', form=form, nav=True)


@app.route("/track/<int:track_id>")
def track(track_id):
	page = request.args.get('page', 1, type=int)
	bpm_window = request.args.get('bpm_window', 2, type=int)
	tracks_per_page = 10
	currenttrack = Track.query.get_or_404(track_id)
	recommendations = Track.query.filter(Track.tempo>=(currenttrack.tempo-1), Track.tempo<=(currenttrack.tempo+1), \
								Track.id!=currenttrack.id).all()
	similarity_recommendations = []
	for item in recommendations:
		item_with_similarity = {'id': item.id, 'title': item.title, 'album': item.album, 'artist': item.artist, 'tempo': item.tempo,
			'year': item.year, 'key': item.key, 'energy': item.energy,
			'similarity': similarity(item.energy, item.key, currenttrack.energy, currenttrack.key)}
		similarity_recommendations.append(item_with_similarity)
	ordered_recommendations = sorted(similarity_recommendations, key=itemgetter('similarity'))
	paginated_recommendations = ordered_recommendations[tracks_per_page*(page-1):tracks_per_page*page]# Python will not let this generate a list index error.
	no_of_pages = round(len(ordered_recommendations)/tracks_per_page+0.5)#The +0.5 makes sure that it is always rounded up to the nearest integer
	return render_template('track.html', title=currenttrack.artist + " - " + currenttrack.title, currenttrack=currenttrack,\
		recommendations=paginated_recommendations, page=page, no_of_pages=no_of_pages, nav=True)


@app.route('/track/<int:track_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_track(track_id):
	track = Track.query.filter_by(id=track_id).first()
	if track.contributor != current_user:
		abort(403)
	split_key = track.key.split()
	form=TrackForm(artist=track.artist, album=track.album, title=track.title, year=track.year,
		tempo=track.tempo, key=split_key[0], mode=split_key[1], energy=track.energy)
	if form.validate_on_submit():
		track.artist = form.artist.data
		track.album = form.album.data
		track.year = form.year.data
		track.title = form.title.data
		track.key = form.key.data + ' ' + form.mode.data
		track.tempo = form.tempo.data
		track.energy = form.energy.data
		db.session.commit()
		flash(track.title + ' by ' + track.artist + ' was updated.', 'success')
		return redirect(url_for('my_contributions', username=current_user.username))
	return render_template('edittrack.html', title='Edit Track ' + str(track_id), form=form, track=track, nav=True)


@app.route('/track/<int:track_id>/delete', methods=['POST'])
@login_required
def delete_track(track_id):
	track = Track.query.filter(Track.id==track_id).first()
	if track.contributor != current_user:
		abort(403)
	db.session.delete(track)
	db.session.commit()
	flash(track.title + ' by ' + track.artist + ' was deleted.', 'success')
	return redirect(url_for('user_contributions', username=current_user.username))


@app.route('/user/<string:username>')
def user(username):
	page = request.args.get('page', 1, type=int)
	username = username
	user = User.query.filter_by(username=username).first()
	user_track_list = Track.query.filter_by(user_id=user.id).paginate(page=page, per_page=10)
	return render_template('user.html', title='User: ' + username, user=user, user_track_list=user_track_list, nav=True)


@app.route('/my_contributions/<string:username>')
@login_required
def my_contributions(username):
	page = request.args.get('page', 1, type=int)
	username = username
	user = User.query.filter_by(username=username).first()
	if user != current_user:
		abort(403)
	user_track_list = Track.query.filter_by(user_id=user.id).paginate(page=page, per_page=10)
	return render_template('my_contributions.html', title='My Contributions', user=user, user_track_list=user_track_list, edit=True, nav=True)


@app.route('/search', methods=['GET', 'POST'])
def search():
	form = SearchForm()
	if form.validate_on_submit():
		search_term = form.search_term.data
		return redirect(url_for('searchresults', search_term=search_term))
	return render_template('search.html', title='Search', form=form, nav=True)


@app.route('/searchresults/<search_term>')
def searchresults(search_term):
	page = request.args.get('page', 1, type=int)
	search_results = Track.query.filter(\
		(Track.artist.contains(search_term)) |\
		(Track.title.contains(search_term)) |\
		(Track.tempo.contains(search_term)) |\
		(Track.key.contains(search_term))\
		).paginate(page=page, per_page=10)# The | acts as an 'or' operator
	return render_template('searchresults.html', search_term=search_term, title="Search for " + search_term, search_results=search_results, nav=True)

def send_reset_email(user):
	token = user.get_reset_token()
	msg = Message('Password Reset Request',
							sender='psychilldb@gmail.com',
							recipients=[user.email])
	msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then ignore this email and no changes will be made.
'''
#_external=True gets an absolute rather than a relative url.
	mail.send(msg)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RequestResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		send_reset_email(user)
		flash('An email has been sent to your email address', 'success')
		return redirect(url_for('login'))
	return render_template('reset_request.html', title='Reset Password', form=form, nav=True)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	user = User.verify_reset_token(token)
	if user is None:
		flash('That is an invalid or expired token', 'danger')
		return redirect(url_for('reset_request'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = hashed_password
		db.session.commit()
		flash(f'Your password has been reset.', 'success')
		return redirect(url_for('login'))
	return render_template('reset_token.html', title='Reset Password', form=form, nav=True)

@app.errorhandler(404)
def error_404(e):
	return render_template('404.html', nav=True), 404

@app.errorhandler(403)
def error_403(e):
	return render_template('403.html', nav=True), 403

@app.errorhandler(500)
def error_500(e):
	return render_template('500.html', nav=True), 500
