import os

from flask import jsonify

import resources
from config import app, db, api
from models import UserModel


@app.route('/')
def index():
    return jsonify({'message': 'Hello, World!'})


@app.before_first_request
def create_tables():
    db_path = app.config['SQLALCHEMY_DATABASE_URI']
    if os.path.exists(db_path):
        os.unlink(app.config['SQLALCHEMY_DATABASE_URI'])
    db.create_all()
    populate_example_data()


def populate_example_data():
    example_users = [('hermione', 'granger'),
                     ('ron', 'weasley'),
                     ('nevil', 'longbottom')]
    for username, password in example_users:
        new_user = UserModel(
            username=username,
            password=UserModel.generate_hash(password)
        )
        try:
            new_user.save_to_db()
        except:
            return


api.add_resource(resources.UserLogin, '/login')
api.add_resource(resources.TokenRefresh, '/token/refresh')
api.add_resource(resources.JsonPatch, '/jsonpatch')
api.add_resource(resources.Thumbnail, '/thumbnail')
