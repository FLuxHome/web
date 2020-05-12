from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SECRET_KEY'] = "0e4b06d2af989abb86f43354266b71d0b7da385156a5e4b7185b84f2a8406048"
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://root:89161442552@localhost/project"
bcrypt_flask = Bcrypt(app)
login_flask = LoginManager(app)
login_flask.login_view = "login"
login_flask.login_message_category = 'alert alert-primary'
db = SQLAlchemy(app)

from Shreddit.root import home, register, login, profile, logout
