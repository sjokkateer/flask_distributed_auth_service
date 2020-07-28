from config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
Migrate(app, db)
ma = Marshmallow(app)


from models import Image
from views import ImageUploadView


app.add_url_rule('/', view_func=ImageUploadView.as_view('image'))
