from app import db
from flask import jsonify, request
from flask.views import MethodView
from schemas import ImageSchema

import jwt
import os
import requests


image_schema = ImageSchema()


class ImageUploadView(MethodView):
    def post(self):
        # verify user's access token by getting
        # the required key by id from auth api
        access_token = get_access_token(request)
        payload = jwt.decode(access_token, verify=False)
        
        key_id = payload.get('key_id')
        url = f"{os.getenv('AUTH_SERVER')}/keys/{key_id}"
        
        response = requests.get(url)
        pub_key = response.json()[f'{key_id}']

        # Crashes on uploading when trying to verify an expired access_token
        try:
            payload = jwt.decode(access_token, pub_key, algorithms='RS256')
        except jwt.exceptions.ExpiredSignatureError as e:
            return jsonify({'message': e.args[0]}), 401
        
        user_id = payload.get('user_id')
        request_data = request.get_json()
        
        if user_id == request_data.get('user_id'):
            image = image_schema.load(request_data)

            db.session.add(image)
            db.session.commit()

            return jsonify({'image': image_schema.dump(image)})
        # Check user's id in claim vs the posted id
        # if that matches, validate the image

        # if that checks out, store the image.
        return jsonify({'message': 'Alive!'})


def get_access_token(request):
    bearer_token = request.headers.get('Authorization')
    # Of course should do some checks normally but lets keep it simple for now
    return bearer_token.split()[-1]
