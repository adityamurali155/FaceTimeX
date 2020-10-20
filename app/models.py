from flask_login import UserMixin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from flask_bcrypt import Bcrypt
from datetime import datetime


db = SQLAlchemy()
bcrypt = Bcrypt()


class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    username = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String)
    password = db.Column(db.String, nullable=True)

    def __init__(self, username, name, password=None):
        self.username = username
        self.name = name
        if password is not None:
            self.password = bcrypt.generate_password_hash(
                password, rounds=10).decode('utf-8')


class OAuth(OAuthConsumerMixin, db.Model):

    __tablename__ = "oauth_sessions"

    provider_user_id = db.Column(db.String)
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    user = relationship(User)


class Candidate(db.Model):

    __tablename__ = "candidates"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    last_attendance = db.Column(db.DateTime, nullable=True)

    name = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    user = relationship(User)

    encoding = db.Column(db.PickleType)


class Attendance(db.Model):

    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())

    description = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    user = relationship(User)


class Record(db.Model):

    __tablename__ = "records"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())

    candidate_id = db.Column(db.Integer, ForeignKey("candidates.id"))
    candidate = relationship(Candidate)

    attendance_id = db.Column(db.Integer, ForeignKey("attendance.id"))
    attendance = relationship(Attendance)

    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    user = relationship(User)
