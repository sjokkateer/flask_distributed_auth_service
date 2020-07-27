from app import db
from classes import JWT, KeyFolder, Token
from flask import jsonify, request
from flask.views import MethodView
from marshmallow import ValidationError
from models import User, Key
from schemas import LoginSchema, UserSchema
from sqlalchemy import exc


user_schema = UserSchema()
login_schema = LoginSchema()


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

            return jsonify({'tokens': JWT.create_tokens(user.id)})
        except ValidationError as e:
            return jsonify({
                'error': e.messages
            })


class RotationKeyView(MethodView):
    def get(self):
        '''
        This would be a good candidate for caching, since most likely the keys will often be requested
        unless an application would cache the keys themselves to validate payloads
        '''
        response = {'keys': []}
        active_keys = Key.get_n_most_recent_keys(3)
        
        for key in active_keys:
            pub_key_file = KeyFolder.get_public_key_folder() / str(key.id)
            response['keys'].append({key.id: open(pub_key_file).read()})

        return jsonify(response)


class RefreshTokenView(MethodView):
    def post(self):
        data = request.get_json()
        refresh_token = data.get('refresh_token')

        if not refresh_token: return jsonify({'message': 'TBD'})

        payload = JWT.decode(refresh_token)
        access_token = JWT.create_token_from_existing_payload(Token.ACCESS, payload)
        
        return jsonify({'access_token': access_token})
