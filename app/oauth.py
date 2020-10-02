from flask import flash, redirect, url_for
from sqlalchemy.orm.exc import NoResultFound
from flask_login import current_user
from flask_dance.consumer import oauth_authorized
from flask_dance.contrib.github import make_github_blueprint
from flask_dance.contrib.google import make_google_blueprint
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage

from app.models import db, OAuth

storage = SQLAlchemyStorage(OAuth, db.session, user=current_user)
github_blueprint = make_github_blueprint(storage=storage)
google_blueprint = make_google_blueprint(storage=storage)


@oauth_authorized.connect_via(github_blueprint)
def github_authorized(blueprint, token):
    if not token:
        msg = "Failed to log in with GitHub."
        flash(msg, category="danger")
        return redirect(url_for('login'))

    resp = blueprint.session.get("/user")
    if not resp.ok:
        msg = "Failed to fetch user info from GitHub."
        flash(msg, category="danger")
        return redirect(url_for('login'))

    github_info = resp.json()
    github_user_id = str(github_info["id"])

    query = OAuth.query.filter_by(
        provider=blueprint.name,
        provider_user_id=github_user_id,
    )

    try:
        oauth = query.one()
    except NoResultFound:
        oauth = OAuth(
            provider=blueprint.name,
            provider_user_id=github_user_id,
            token=token,
        )

    if oauth.user:
        login_user(oauth.user)
    else:
        user = User(
            username=github_info["login"],
            name=github_info["name"],
        )
        oauth.user = user
        db.session.add_all([user, oauth])
        db.session.commit()
        login_user(user)

    flash("Successfully signed in with GitHub.", category="success")
    return redirect(url_for('index'))


@oauth_authorized.connect_via(google_blueprint)
def google_authorized(blueprint, token):
    if not token:
        msg = "Failed to log in with Google."
        flash(msg, category="danger")
        return redirect(url_for('login'))

    resp = blueprint.session.get("/oauth2/v1/userinfo")
    if not resp.ok:
        msg = "Failed to fetch user info from Google."
        flash(msg, category="danger")
        return redirect(url_for('login'))

    google_info = resp.json()
    google_user_id = str(google_info["id"])

    query = OAuth.query.filter_by(
        provider=blueprint.name,
        provider_user_id=google_user_id,
    )

    try:
        oauth = query.one()
    except NoResultFound:
        oauth = OAuth(
            provider=blueprint.name,
            provider_user_id=google_user_id,
            token=token,
        )

    if oauth.user:
        login_user(oauth.user)
    else:
        user = User(
            username=google_info["email"],
            name=google_info["name"],
        )
        oauth.user = user
        db.session.add_all([user, oauth])
        db.session.commit()
        login_user(user)

    flash("Successfully signed in with Google.", category="success")
    return redirect(url_for('index'))
