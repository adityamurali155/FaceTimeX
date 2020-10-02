from flask_login import UserMixin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
bcrypt = Bcrypt()


class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    name = db.Column(db.String)
    password = db.Column(db.String)

    def __init__(self, username, name, password):
        self.username = username
        self.name = name
        self.password = bcrypt.generate_password_hash(password, rounds=10)


class OAuth(OAuthConsumerMixin, db.Model):

    __tablename__ = "oauth_sessions"

    provider_user_id = db.Column(db.String)
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    user = relationship(User)
