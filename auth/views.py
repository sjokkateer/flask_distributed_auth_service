from auth import schemas
from auth.app import db
from flask import jsonify, request
from flask.views import MethodView
from marshmallow import ValidationError
from sqlalchemy import exc


user_schema = schemas.UserSchema()


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
