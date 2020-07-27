from config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)


from models import User, Key
from views import LoginView, RefreshTokenView, RegistrationView, RotationKeyView

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Key': Key}

# Routes go here
app.add_url_rule('/login', view_func=LoginView.as_view('login'))
app.add_url_rule('/register', view_func=RegistrationView.as_view('register'))
app.add_url_rule('/keys', view_func=RotationKeyView.as_view('keys'))
app.add_url_rule('/refresh', view_func=RefreshTokenView.as_view('refresh'))
