from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '102da341b643882293e4ddd96d514b8f4505e5df211224c581ac4ea558206856'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///erp.db'

database = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'alert-info'

from ERP import routes