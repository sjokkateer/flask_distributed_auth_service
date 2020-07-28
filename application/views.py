from classes import LoginClient, User
from enum import Enum
from flask import redirect, render_template, request, session, url_for
from flask.views import View, MethodView
from flask_login import login_user, current_user
from forms import LoginForm
from functools import wraps


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
            data = LoginClient.login(form.data['email'], form.data['password'])
            
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

        return 'you wish'
