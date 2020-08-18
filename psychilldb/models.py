from psychilldb import db, login_manager, app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(120), unique=False, nullable=False)
	email = db.Column(db.String(120), unique=False, nullable=False)
	password = db.Column(db.String(60), nullable=False)
	tracks = db.relationship('Track', backref='contributor', lazy=True)# 'lazy=True' means that SQL will load all the tracks by that user in one go when requested

	def get_reset_token(self, expires_sec=1800):
		s = Serializer(app.config['SECRET_KEY'], expires_sec)
		return s.dumps({'user_id': self.id}).decode('utf-8')
	
	@staticmethod
	def verify_reset_token(token):
		s = Serializer(app.config['SECRET_KEY'])
		try:
			user_id = s.loads(token)['user_id']
		except:
			return None
		return User.query.get(user_id)

	def __repr__(self):
		return f"User('{self.username}', '{self.email}')"


class Track(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	artist = db.Column(db.String(120), unique=False, nullable=False)
	album = db.Column(db.String(120), unique=False, nullable=False)
	title = db.Column(db.String(120), unique=False, nullable=False)
	year = db.Column(db.Integer, unique=False, nullable=False)
	tempo = db.Column(db.Integer, unique=False, nullable=False)
	key = db.Column(db.String(20), unique=False, nullable=False)
	energy = db.Column(db.Integer, unique=False, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)# here user has a lowercase U as we are referencing the table and column name rather than the class

	def __repr__(self):
		return f"Track('{self.artist}', '{self.album}', '{self.title}', '{self.year}', '{self.tempo}', '{self.key}', '{self.energy}')"


