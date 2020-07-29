from flask import session
from flask_login import UserMixin

import os
import requests
import enum


class RequestMethod(enum.Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    DELETE = 'DELETE'


class StatusCode(enum.Enum):
    OK = 200
    UNAUTHORIZED = 401
    NOT_FOUND = 404


# Rename to AuthClient or something such that it will also handle refresh
class LoginClient:
    @staticmethod
    def login(email, password):
        url = f'{LoginClient.get_host()}/login'
        response = BaseRequest.make(url, RequestMethod.POST, {
            'email': email,
            'password': password
        })
        
        return response

    @staticmethod
    def refresh():
        url = f'{LoginClient.get_host()}/refresh'

        response = BaseRequest.make(url, method=RequestMethod.GET, headers={
            'Authorization': AuthenticatedRequest.create_bearer_token(session.get('refresh_token'))
        })

        if response.status_code == StatusCode.OK.value:
            session['access_token'] = response.json()['access_token']
        else:
            raise Exception


    @staticmethod
    def get_host() -> str:
        return os.getenv('AUTH_SERVER')


class BaseRequest:
    @classmethod
    def make(cls, url, method=None, json=None, headers={}):
        if method == RequestMethod.PATCH:
            response = requests.patch(url, json=json, headers=headers)
        elif method == RequestMethod.POST:
            response = requests.post(url, json=json, headers=headers)
        elif method == RequestMethod.PUT:
            response = requests.put(url, json=json, headers=headers)
        elif method == RequestMethod.DELETE:
            response = requests.delete(url, json=json, headers=headers)
        else:
            response = requests.get(url, json=json, headers=headers)
        
        return response


class AuthenticatedRequest(BaseRequest):
    @classmethod
    def make(cls, url, method=None, json=None, headers={}):
        headers['Authorization'] = cls.create_bearer_token(session.get('access_token'))
        response = super().make(url, method, json, headers)

        if response.status_code == StatusCode.UNAUTHORIZED.value:
            LoginClient.refresh()
            cls.make(url, method, json, headers)

        return response

    @classmethod
    def create_bearer_token(cls, token):
        return f'Bearer {token}'


class User(UserMixin):
    def __init__(self, id, email=None, first_name=None, last_name=None, joined_at=None):
        self.id = id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.joined_at = joined_at

    @staticmethod
    def from_data(user_data):
        data = {
            'id': user_data['id'], 
            'email': user_data['email'],
            'joined_at': user_data['joined_at'],
        }

        profile = user_data.get('profile')

        if profile:
            data['first_name'] = profile.get('first_name')
            data['last_name'] = profile.get('last_name')

        return User(**data)