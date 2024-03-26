import os
import uuid

from flask import *
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jwt
from http import HTTPStatus
from werkzeug.utils import secure_filename
from models import User, Image, VideoFrame, Music, Video
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
                user_id=current_user.id
            )
            db.session.add(frame)
            db.session.commit()
    return make_response(jsonify({"message": "Images Saved"}), HTTPStatus.OK)


@app.route('/getMyImages', methods=['GET'])
@token_required
def get_my_images(current_user):
    images = Image.query.filter_by(user_id=current_user.id).all()
    print(images)
    image_list  = []
    for image in images:
        image_list.append({"name": image.image_path, "user": image.user_id, "id": image.id})
    if images is not None:
        return make_response(jsonify({"images": image_list}), HTTPStatus.OK)
    return make_response(jsonify({"message": "No Images Uploaded"}), HTTPStatus.BAD_REQUEST)


@app.route('/uploadAudio', methods=['POST'])
@token_required
def upload_audio(current_user):
    if len(request.files) == 0:
        return make_response(jsonify({"message": "No files sent"}), HTTPStatus.BAD_REQUEST)
    image_files = request.files
    for file in image_files.values():
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['BASE_MUSIC_DIR'], filename))
            frame = Music(
                music_path=os.path.join(app.config['BASE_MUSIC_DIR'], filename),
                user_id=current_user.id
            )
            db.session.add(frame)
            db.session.commit()
    return make_response(jsonify({"message": "Music Saved"}), HTTPStatus.OK)


@app.route('/setVideoOptions', methods=['POST'])
@token_required
def setVideoOptions(current_user):
    print(len(request.files))
    print(request.files.values())
    print(request.form)
    # return make_response(jsonify({"message": "Images Saved"}), HTTPStatus.OK)
    # print(request.files.keys())
    if len(request.files) == 0:
        return make_response(jsonify({"message": "No Images Selected"}), HTTPStatus.BAD_REQUEST)
    image_files = request.files
    music_path = ""
    for file in image_files.values():
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['BASE_MUSIC_DIR'], filename))
            frame = Music(
                music_path=os.path.join(app.config['BASE_MUSIC_DIR'], filename),
                user_id=current_user.id
            )
            music_path = frame.music_path
            db.session.add(frame)
            db.session.commit()
    newVideo = Video(
        user_id=current_user.id,
        name=os.path.join(app.config['BASE_VIDEO_DIR'], current_user.name)+".mp4",
        music=Music.query.filter_by(music_path=music_path).first().id
    )
    for imgID in request.form['Image Ids'].split(','):
        img = Image.query.filter_by(id=int(imgID)).first()
        frame = VideoFrame(
            img_path=img.image_path,
            img_duration=int(request.form['imgDuration']),
            img_key=int(img.id)
        )
        db.session.add(frame)
        newVideo.frames.append(frame)
    db.session.add(newVideo)
    db.session.commit()
    return make_response(jsonify({"message": "Video Options Saved"}), HTTPStatus.OK)


@app.route('/getVF', methods=['GET'])
@token_required
def getVF(current_user):
    video = Video.query.filter_by(user_id=current_user.id).first()
    # print(images)
    image_list = []
    for frame in video.frames:
        image_list.append({"path": frame.img_path})
    if not image_list:
        return make_response(jsonify({"message": "No Video Frames Found"}), HTTPStatus.BAD_REQUEST)
    return make_response(jsonify({"images": image_list}), HTTPStatus.OK)


@app.route('/createVid', methods=['GET'])
@token_required
def createVid(current_user):
    import cv2
    from moviepy.editor import VideoFileClip, AudioFileClip

    video = Video.query.filter_by(user_id=current_user.id).first()
    audio_clip = AudioFileClip(Music.query.filter_by(id=video.music).first().music_path)
    video_filename = video.name
    print(video_filename)
    first_image = cv2.imread(video.frames[0].img_path)
    h, w, _ = first_image.shape

    codec = cv2.VideoWriter_fourcc(*'mp4v')
    vid_writer = cv2.VideoWriter(video_filename, codec, 1, (w, h))

    for img in video.frames:
        # print(img.img_path)
        loaded_img = cv2.imread(img.img_path)
        loaded_img = cv2.resize(loaded_img, (w, h), interpolation=cv2.INTER_LINEAR)
        for _ in range(img.img_duration):
            # print(loaded_img)
            vid_writer.write(loaded_img)

    clipped_audio = audio_clip.subclip(0, video.frames[0].img_duration*len(video.frames))
    vid_writer.release()

    video_clip = VideoFileClip(video.name)
    video_with_audio = video_clip.set_audio(clipped_audio)
    video_with_audio.write_videofile(video.name, codec='libx264', audio_codec='aac')
    res_files = []
    resolutions = [360, 720, 1080]
    for resolution in resolutions:
        import moviepy.editor as mp
        clip = mp.VideoFileClip(video.name)
        clip_resized = clip.resize(height=resolution)
        new_filename = video.name[:-4]+"_"+str(resolution)+".mp4"
        clip_resized.write_videofile(new_filename)
        res_files.append(new_filename)

    return make_response(jsonify({"message": "video created", "path": video.name, "res_paths": res_files}))


@app.route('/setUpVidDownload', methods=['POST'])
@token_required
def vidDownload(current_user):
    import moviepy.editor as mp
    resolution = int(request.form['resolution'])
    video = Video.query.filter_by(user_id=current_user.id).first()
    clip = mp.VideoFileClip(video.name)
    clip_resized = clip.resize(height=resolution)
    new_filename = video.name[:-4]+"_"+str(resolution)+".mp4"
    clip_resized.write_videofile(new_filename)
    return make_response(jsonify({"path": new_filename}))


def create_app():
    app.config['SECRET_KEY'] = "my secret key"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database.db'
    app.config['BASE_IMAGE_DIR'] = './images/'
    app.config['BASE_VIDEO_DIR'] = './videos/'
    app.config['BASE_MUSIC_DIR'] = './music/'
    db.init_app(app)


if __name__ == '__main__':
    create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
