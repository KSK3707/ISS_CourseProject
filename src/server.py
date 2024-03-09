import os
import uuid

from flask import *
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jwt
from http import HTTPStatus
from werkzeug.utils import secure_filename
from models import User, Image, VideoFrame
from database import db


app = Flask(__name__)
cors = CORS(app)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return make_response(jsonify({'message': 'Token is missing !!'}), HTTPStatus.UNAUTHORIZED)

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],algorithms=['HS256'])
            current_user = User.query.filter_by(username=data['username']).first()
        except Exception as e:
            return make_response(jsonify({'message': 'Token is invalid !!'}), HTTPStatus.UNAUTHORIZED)
        return f(current_user, *args, **kwargs)

    return decorated


@app.route('/signup', methods=['POST'])
def signup():
    name = request.json["name"]
    username = request.json["username"]
    email = request.json["email"]
    password = request.json["password"]
    if not name or not username or not email or not password:
        return make_response(jsonify({"message": "Please fill all fields"}), HTTPStatus.BAD_REQUEST)
    curr_user = User.query.filter_by(email=email).first()
    if curr_user is not None:
        return make_response(jsonify({"message": "User Already Exists"}), HTTPStatus.OK)
    else:
        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            username=username
        )
        db.session.add(user)
        db.session.commit()
        return make_response(jsonify({"message": "User created"}), HTTPStatus.OK)


@app.route('/login', methods=['POST'])
def login():
    email = request.json['email']
    password = request.json['password']
    if not email or not password:
        make_response(jsonify({"message": "Invalid Request"}), HTTPStatus.BAD_REQUEST)
    user = User.query.filter_by(email=email).first()
    if user is None:
        return make_response(jsonify({"message": "User not found"}), HTTPStatus.NOT_FOUND)
    if check_password_hash(user.password, password):
        token = jwt.encode({
            'username': user.username
        }, app.config.get('SECRET_KEY'))
        return make_response(jsonify({'jwt-token': token}), HTTPStatus.OK)
    else:
        return make_response(jsonify({"message": "Invalid Password"}), HTTPStatus.FORBIDDEN)


@app.route('/uploadImage', methods=['POST'])
@token_required
def upload_image(current_user):
    # print(request.files.keys())
    if len(request.files) == 0:
        return make_response(jsonify({"message": "No files sent"}), HTTPStatus.BAD_REQUEST)
    image_files = request.files
    for file in image_files.values():
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['BASE_IMAGE_DIR'], filename))
            frame = Image(
                image_path=os.path.join(app.config['BASE_IMAGE_DIR'], filename),
            )
            db.session.add(frame)
            db.session.commit()
    return make_response(jsonify({"message": "Images Saved"}), HTTPStatus.OK)


def create_app():
    app.config['SECRET_KEY'] = "my secret key"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database.db'
    app.config['BASE_IMAGE_DIR'] = './images/'
    app.config['BASE_VIDEO_DIR'] = './videos/'
    db.init_app(app)


if __name__ == '__main__':
    create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
