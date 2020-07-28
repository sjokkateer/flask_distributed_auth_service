from classes import JWT, TokenExtractor
from flask import request, jsonify

import jwt


def get_payload_from_token(request):
    access_token = TokenExtractor.extract(request)
    return JWT.decode(access_token)


def verify_token_and_user_resource_access(function):
    def wrapper(*args, **kwargs):
        try:
            payload = get_payload_from_token(request)
        except jwt.exceptions.ExpiredSignatureError as e:
            return jsonify({'message': e.args[0]}), 401
        except NoTokenException as e:
            return jsonify({'message': e.args[0]}), 403

        if payload.get('user_id') != kwargs.get('id'): 
            return jsonify({'message': 'This is not your resource, friend.'}), 401

        return function(*args, **kwargs)

    return wrapper
