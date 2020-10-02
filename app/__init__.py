import os
from flask import Flask, render_template, flash, request, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required


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


@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if not request.form["username"] or request.form["username"] == "":
            flash("Username cannot be empty!", category="danger")
        elif not request.form["password"] or request.form["password"] == "":
            flash("Password cannot be empty!", category="danger")
        else:
            user = User.query.filter_by(
                username=request.form["username"]
            ).first()
            if bcrypt.check_password_hash(user.password, request.form["password"]):
                login_user(user)
                flash("Successfully signed in!", category="success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid Credentials!", category="danger")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        if not request.form["username"] or request.form["username"] == "":
            flash("Username cannot be empty!", category="danger")
        elif User.query.filter_by(username=request.form["username"]).first() is not None:
            flash("Username already exists!", category="danger")
        elif not request.form["name"] or request.form["name"] == "":
            flash("Name cannot be empty!", category="danger")
        elif not request.form["password"] or request.form["password"] == "":
            flash("Password cannot be empty!", category="danger")
        elif not request.form["confirm_password"] or request.form["password"] != request.form["confirm_password"]:
            flash("Passwords should match!", category="danger")
        else:
            user = User(
                username=request.form["username"],
                name=request.form["name"],
                password=request.form["password"]
            )
            db.session.add(user)
            db.session.commit()
            flash("Sign up successful!", category="success")
            return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    flash('Logout successful', category='success')
    return redirect(url_for('login'))
