from models import User
from schemas import LoginSchema, UserSchema
from app import db
from classes import JWT
from flask import jsonify, request
from flask.views import MethodView
from marshmallow import ValidationError
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
