from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///psychilldb.db'
app.config['SECRET_KEY'] = 'the_secret_key'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'# This tells the extension where the login route is located
login_manager.login_message_category = 'info'# This sets the bootstrap class for the 'login needed' message
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'psychilldb@gmail.com'
app.config['MAIL_PASSWORD'] = 'Carthag13'
mail = Mail(app)

from psychilldb import routes