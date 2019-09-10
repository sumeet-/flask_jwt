import io
import json

import jsonpatch as jsonpatch
import jsonpointer
import requests
from PIL import Image
from flask import make_response, Response
from flask_restful import Resource, reqparse
from flask_jwt_extended import (create_access_token,
                                create_refresh_token,
                                jwt_required,
                                jwt_refresh_token_required,
                                get_jwt_identity,
                                get_raw_jwt)
from models import UserModel


class UserLogin(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username', help='This field cannot be blank', required=True)
    parser.add_argument('password', help='This field cannot be blank', required=True)

    def post(self):
        data = self.parser.parse_args()
        username = data['username']
        password = data['password']
        current_user = UserModel.query.filter_by(username=username).first()
        if not current_user:
            return {'message': f'User {username} doesn\'t exist'}

        if UserModel.verify_hash(password, current_user.password):
            access_token = create_access_token(identity=username)
            refresh_token = create_refresh_token(identity=username)
            return {'message': f'Logged in as {current_user.username}',
                    'access_token': access_token,
                    'refresh_token': refresh_token
                    }
        else:
            return make_response({'message': 'Wrong credentials'}, 401)


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {'access_token': access_token}


class JsonPatch(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('json_object', help='This field cannot be blank', required=True)
    parser.add_argument('json_patch', help='This field cannot be blank', required=True)

    @jwt_required
    def post(self):
        data = self.parser.parse_args()
        json_object = json.loads(data['json_object'])
        json_patch = data['json_patch']
        try:
            return jsonpatch.apply_patch(json_object, json_patch)
        except (jsonpatch.JsonPatchException, jsonpointer.JsonPointerException):
            return make_response('Invalid JSON Patch', 400)


class Thumbnail(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('image_url', help='This field cannot be blank', required=True)
    thumbnail_size = (50, 50)
    @jwt_required
    def post(self):
        data = self.parser.parse_args()
        image_url = data['image_url']
        response = requests.get(image_url)
        content_type = response.headers['Content-Type']
        img_format = content_type.split('/')[-1]
        print(img_format)
        if img_format.lower() not in ['png', 'jpg', 'jpeg']:
            return make_response('Invalid File Format', 400)

        img_pil = Image.open(io.BytesIO(response.content))
        img_pil.thumbnail(self.thumbnail_size)
        buf = io.BytesIO()
        img_pil.save(buf, format=img_format)
        buf.seek(0)
        thumbnail = buf.read()
        response = make_response(thumbnail)
        response.headers['Content-Type'] = content_type
        return response
