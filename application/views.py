from classes import LoginClient, User, AuthenticatedRequest, RequestMethod, StatusCode
from enum import Enum
from flask import flash, redirect, render_template, request, session, url_for
from flask.views import View, MethodView
from flask_login import login_user, current_user
from forms import LoginForm, ImageForm
from functools import wraps

import base64
import os
import requests


class HttpMethods(Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    DELETE = 'DELETE'


class TemplateView(View):
    methods = [HttpMethods.GET.value]

    def __init__(self, template_name):
        self.template_name = template_name

    def dispatch_request(self):
        return render_template(self.template_name)


def already_authenticated(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        return function(*args, **kwargs)

    return wrapper


class LoginView(MethodView):
    decorators = [already_authenticated]

    def get(self):
        return render_template('login.html', form=LoginForm())

    def post(self):
        form = LoginForm()

        if form.validate_on_submit():
            data = LoginClient.login(form.data['email'], form.data['password']).json()
            
            if not 'error' in data:
                session['access_token'] = data['tokens']['access_token']
                session['refresh_token'] = data['tokens']['refresh_token']
                
                user = User.from_data(data['user'])
                session[user.id] = user

                login_user(user)

                # unsafe
                url = request.args.get('next', '/')
                
                return redirect(url)
                # else we got an error

        # Finally, invalid info
        return redirect(url_for('login', next=request.args.get('next', '/')))


def clear_previous_session_image(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        uploaded_image = session.get('uploaded_image')
        
        if uploaded_image:
            counter = session.get('display_counter', 0)
            session['display_counter'] = counter + 1

            if session['display_counter'] > 1:
                session.pop('uploaded_image', None)

        return function(*args, **kwargs)
    
    return wrapper


class ImageUploadView(MethodView):
    decorators = [clear_previous_session_image]

    def get(self):
        return render_template('image-upload.html', form=ImageForm())

    def post(self):
        form = ImageForm()

        if form.validate_on_submit():
            image = form.image.data.stream.read()
            string_image = f'data:{form.image.data.mimetype};base64,' + base64.b64encode(image).decode('utf-8')

            url = f"{os.getenv('IMG_SERVER')}/"
            data = {
                'user_id': current_user.id,
                'title': form.data.get('title'),
                'image': string_image
            }
            
            response = AuthenticatedRequest.make(url, method=RequestMethod.POST, json=data)

            if response.status_code == 200:
                flash(f"Image {data['title']} successfully uploaded!")
                
                session['uploaded_image'] = response.json()['image']
                session['display_counter'] = 0

                return redirect(url_for('image'))

        return 'Something went wrong'

class ImagesView(MethodView):
    def get(self):
        images = []
        url = f"{os.getenv('IMG_SERVER')}/"
        response = AuthenticatedRequest.make(url, method=RequestMethod.GET)

        if response.status_code == StatusCode.OK.value:
            images = response.json().get('images')
        
        return render_template('images.html', images=images)

