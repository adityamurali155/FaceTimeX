import os
from flask import Flask, render_template
from flask_login import LoginManager, logout_user, login_required


from app.config import Config
from app.models import db, bcrypt, User
from app.oauth import github_blueprint, google_blueprint

app = Flask(__name__)
app.config.from_object(Config)
bcrypt.init_app(app)
db.init_app(app)

with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.login_message = "Login to access this page"
login_manager.login_message_category = "warning"
login_manager.login_view = "login"
login_manager.init_app(app)

app.register_blueprint(github_blueprint)
app.register_blueprint(google_blueprint)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")


@app.route("/signup", methods=["GET"])
def signup():
    return render_template("signup.html")


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    flash('Logout successful', category='success')
    return render_template("index.html")
