from .config import Config
from .views import LoginView, TemplateView
from classes import User
from datetime import datetime
from flask import Flask, flash, render_template, redirect, session, url_for
from flask_login import LoginManager, login_required, logout_user
from flask_session import Session

import jwt
import requests


app = Flask(__name__)
app.config.from_object(Config)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Hey, please first log in to access this page.'
Session(app)


@login_manager.user_loader
def load_user(user_id):
    refresh_token = session.get('refresh_token')
    payload = jwt.decode(refresh_token, verify=False)

    now = datetime.now()

    if payload['exp'] >= now:
        access_token = session.get('access_token')
        # make the request with the access token, if expired make request for 
        # refresh, getting us a new access_token, making the same request as before
        return User(user_id)
    
    return None



@app.route('/logout')
def logout():
    logout_user()
    flash('See you next time!')
    return redirect(url_for('index'))


app.add_url_rule('/', view_func=TemplateView.as_view('index', template_name='index.html'))
app.add_url_rule('/login', view_func=LoginView.as_view('login'))

something_view = login_required(TemplateView.as_view('something', template_name='something.html'))
app.add_url_rule('/some-page', view_func=something_view)
