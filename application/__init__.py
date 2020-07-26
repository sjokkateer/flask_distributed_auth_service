from .config import Config
from .views import TemplateView
from flask import Flask, render_template


app = Flask(__name__)
app.config.from_object(Config)
app.add_url_rule('/', view_func=TemplateView.as_view('index', template_name='index.html'))
