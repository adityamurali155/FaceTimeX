import os


class Config(object):

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///:memory:"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get(
        "SECRET_KEY", "averysecretkey"
    )
    GITHUB_OAUTH_CLIENT_ID = os.environ.get(
        "GITHUB_OAUTH_CLIENT_ID"
    )
    GITHUB_OAUTH_CLIENT_SECRET = os.environ.get(
        "GITHUB_OAUTH_CLIENT_SECRET"
    )
    GOOGLE_OAUTH_CLIENT_ID = os.environ.get(
        "GOOGLE_OAUTH_CLIENT_ID"
    )
    GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get(
        "GOOGLE_OAUTH_CLIENT_SECRET"
    )
