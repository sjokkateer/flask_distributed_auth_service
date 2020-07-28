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
    def __init__(self, id):
        self.id = id
