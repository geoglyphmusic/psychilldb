from flask_wtf import FlaskForm
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, IntegerField, SubmitField, TextAreaField, SelectField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from psychilldb.models import Track, User


class TrackForm(FlaskForm):
	artist = StringField('Artist', validators=[DataRequired()])
	album = StringField('Album', validators=[DataRequired()])
	title = StringField('Title', validators=[DataRequired()])
	year = IntegerField('Year', validators=[DataRequired()])
	key = SelectField('Key', choices=[('A','A'), ('A#/Gb','A#/Gb'), ('B','B'), ('C','C'), ('C#/Db','C#/Db'), ('D','D'), ('D#/Eb','D#/Eb'), \
													('E','E'), ('F','F'), ('F#/Gb','F#/Gb'), ('G','G'), ('G#/Ab','G#/Ab')], validators=[DataRequired()])
	mode = SelectField('Mode', choices=[('Major', 'Major'), ('Minor','Minor')], validators=[DataRequired()]) # Later options might include ('Dorian','Dorian'), ('Phrygian','Phrygian'), ('Lydian','Lydian'), ('Mixolydian','Mixolydian'), ('Aeolian','Aeolian'), ('Locrian','Locrian'), ('Major Phryigan','Major Phrygian')
	
	tempo = StringField('Tempo', validators=[DataRequired()])
	energy = SelectField('Energy', choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], validators=[DataRequired()])
	
	submit = SubmitField('Submit')

	# def validate_track(self, title):# FlaskForm's validate_on_submit automatically checks for functions beginning with 'validate_'
		# track = Track.query.filter_by(title=title.data).first()
		# if track:
			# raise ValidationError(artist.data + ' - ' + title.data + ' - is already in the database.')


class SearchForm(FlaskForm):
	search_term = StringField('Search', validators=[DataRequired()])
	
	submit = SubmitField('Submit')

	
class UploadForm(FlaskForm):
	file = FileField('Upload an ODS file', validators=[DataRequired(), FileAllowed(['ods'])])
	
	submit = SubmitField('Submit')

	
class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Sign Up')
	
	def validate_username(self, username):# FlaskForm's validate_on_submit automatically checks for functions beginning with 'validate_'
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('That username is taken. Please choose a different one.')
	
	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember = BooleanField('Remember Me')
	submit = SubmitField('Login')
	

class UpdateAccountForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	submit = SubmitField('Update')
	
	def validate_username(self, username):# FlaskForm's validate_on_submit automatically checks for functions beginning with 'validate_'
		if username.data != current_user.username:
			user = User.query.filter_by(username=username.data).first()
			if user:
				raise ValidationError('That username is taken. Please choose a different one.')
	
	def validate_email(self, email):
		if email.data != current_user.email:
			user = User.query.filter_by(email=email.data).first()
			if user:
				raise ValidationError('That email is taken. Please choose a different one.')
				
class UpdatePasswordForm(FlaskForm):
	old_password = PasswordField('Old Password', validators=[DataRequired()])
	new_password = PasswordField('New Password', validators=[DataRequired()])
	confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
	submit = SubmitField('Update')
	
class RequestResetForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	submit = SubmitField('Request Password Reset')
	
	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is None:
			raise ValidationError('There is no account with that email address. You must register first.')
			
class ResetPasswordForm(FlaskForm):
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Reset password')