from auth.config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)


from auth import models
from auth import views

# Routes go here
app.add_url_rule('/register', view_func=views.RegistrationView.as_view('register'))
