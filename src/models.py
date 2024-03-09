from sqlalchemy import ForeignKey
from database import db


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(100))
    email = db.Column(db.String(70), unique=True)
    password = db.Column(db.String(80))


class Image(db.Model):
    __tablename__ = "Image"
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String)


class VideoFrame(db.Model):
    __tablename__ = "video_frame"
    id = db.Column(db.Integer, primary_key=True)
    img_path = db.Column(db.String)
    img_duration = db.Column(db.Integer)
    img_key = db.Column(db.Integer, ForeignKey(Image.id))


video_to_frame_table = db.Table('video_to_frame_table',
                                db.Column('video_id', db.Integer, db.ForeignKey('video.id')),
                                db.Column('image_id', db.Integer, db.ForeignKey('video_frame.id'))
                                )


class Video(db.Model):
    __tablename__ = "video"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey(User.id))
    name = db.Column(db.String(80))
    frames = db.relationship("VideoFrame",
                             secondary=video_to_frame_table)


class Music(db.Model):
    __tablename__ = "music"
    id = db.Column(db.Integer, primary_key=True)
    music_path = db.Column(db.String)
    duration = db.Column(db.Integer)

