from app import db
from classes import AccessToken, TokenService, KeyFileReader, NoTokenException
from datetime import datetime
from decorators import get_payload_from_token
from flask import jsonify, request
from flask.views import MethodView
from marshmallow import ValidationError
from models import User, Profile, Key
from schemas import LoginSchema, UserSchema, ProfileSchema
from sqlalchemy import exc

import jwt


user_schema = UserSchema()
login_schema = LoginSchema()
profile_schema = ProfileSchema()


class RegistrationView(MethodView):
    def post(self):
        user = None

        try:
            data = request.get_json()
            # if data valid, send activation e-mail to user
            user = user_schema.load(data)
            db.session.add(user)
            db.session.commit()
            
            return jsonify({'user': user_schema.dump(user)})
        except ValidationError as e:
            return jsonify({
                'error': e.messages
            })
        except exc.IntegrityError as e:
            return jsonify({
                'error': {
                    'user': f"'{user.email}' already exists."
                }
            })


class LoginView(MethodView):
    def post(self):
        try:
            data = request.get_json()
            validated_data = login_schema.load(data)

            user = User.query.filter_by(email=validated_data['email']).first()
            
            if not user: return jsonify({'error': f"'{validated_data['email']}' is not registered."})

            if not user.is_valid(validated_data['password']): return jsonify({'error': 'Incorrect password!'})

            return jsonify({
                'tokens': TokenService.create_tokens({
                    'user_id': user.id,
                    'exp': datetime.now()
                }),
                'user': user_schema.dump(user)
            })
        except ValidationError as e:
            return jsonify({
                'error': e.messages
            })


class RotationKeyView(MethodView):
    def get(self, key_id):
        '''
        This would be a good candidate for caching, since most likely the keys will often be requested
        unless an application would cache the keys themselves to validate payloads
        '''
        active_keys = Key.get_n_most_recent_keys(3)

        if key_id is None:
            response = {'keys': []}
            
            for key in active_keys:
                response['keys'].append({key.id: KeyFileReader.get_public_key(str(key.id))})
        else:
            if key_id not in [key.id for key in active_keys]: return jsonify({'message': f'Key with {key_id} not found.'}), 404
            
            response = {key_id: KeyFileReader.get_public_key(str(key.id))}

        return jsonify(response)


class RefreshTokenView(MethodView):
    def get(self):
        try:
            payload = get_payload_from_token(request)
            TokenService.selected_token = AccessToken
            access_token = TokenService.create_token({
                'user_id': payload['user_id'],
                'exp': datetime.now(),
            })
        
            return jsonify({'access_token': access_token})
        except jwt.exceptions.ExpiredSignatureError as e:
            return jsonify({'message': e.args[0]}), 401
        except NoTokenException as e:
            return jsonify({'message': e.args[0]}), 403


class UserView(MethodView):
    def get(self, id: int):
        target_user = User.query.get(id)
        
        return jsonify({'user': user_schema.dump(target_user)})
