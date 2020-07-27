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
import commands
import routes


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Key': Key}
