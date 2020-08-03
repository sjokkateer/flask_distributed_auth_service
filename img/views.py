from app import db
from flask import jsonify, request
from flask.views import MethodView
from models import Image
from schemas import ImageSchema

import jwt
import os
import requests


image_schema = ImageSchema()
images_schema = ImageSchema(many=True)

algorithms='RS256'


class ImageUploadView(MethodView):
    def get(self):
        '''
        Endpoint returns the images for user with user_id
        '''
        access_token = get_access_token(request)
        public_key = get_public_key(access_token)

        try:
            payload = jwt.decode(access_token, public_key, algorithms=algorithms)
        except jwt.exceptions.ExpiredSignatureError as e:
            return jsonify({'message': e.args[0]}), 401

        user_id = payload.get('user_id')
        images = Image.query.filter_by(user_id=user_id).order_by(Image.uploaded_at.desc()).limit(10).all()

        return jsonify({'images': images_schema.dump(images)})

    def post(self):
        '''
        Endpoint for user with user_id to upload new images
        '''
        access_token = get_access_token(request)
        public_key = get_public_key(access_token)

        try:
            payload = jwt.decode(access_token, public_key, algorithms=algorithms)
        except jwt.exceptions.ExpiredSignatureError as e:
            return jsonify({'message': e.args[0]}), 401
        
        user_id = payload.get('user_id')
        request_data = request.get_json()
        
        if user_id == request_data.get('user_id'):
            image = image_schema.load(request_data)

            db.session.add(image)
            db.session.commit()

            return jsonify({'image': image_schema.dump(image)})

        return jsonify({'message': 'Something went wrong'})


def get_access_token(request):
    bearer_token = request.headers.get('Authorization')
    # Of course should do some checks normally but lets keep it simple for now
    return bearer_token.split()[-1]

def get_public_key(access_token):
    payload = jwt.decode(access_token, verify=False)
    
    # In the future this should also make use of the token refreshing mechanism
    key_id = payload.get('key_id')
    url = f"{os.getenv('AUTH_SERVER')}/keys/{key_id}"
        
    response = requests.get(url)
    return response.json()[f'{key_id}']
