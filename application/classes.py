from flask_login import UserMixin

import os
import requests
import enum


class StatusCode(enum.Enum):
    OK = 200
    NOT_FOUND = 404


class LoginClient:
    @staticmethod
    def login(email, password):
        url = f'{LoginClient.get_host()}/login'
        response = requests.post(url, json={
            'email': email,
            'password': password
        })

        if response.status_code == StatusCode.OK.value:
            return response.json()

    @staticmethod
    def get_host() -> str:
        return os.getenv('AUTH_SERVER')


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