from enum import Enum
from flask import render_template
from flask.views import View


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

