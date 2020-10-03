import os
import pickle
from flask import Flask, render_template, flash, request, redirect, url_for
from flask_login import current_user, LoginManager, login_user, logout_user, login_required
from flask_qrcode import QRcode
import face_recognition

from app.config import Config
from app.models import db, bcrypt, User, Attendance
from app.oauth import github_blueprint, google_blueprint

app = Flask(__name__)
app.config.from_object(Config)
bcrypt.init_app(app)
db.init_app(app)
qrcode = QRcode(app)

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
    setup_face = False
    face_encoding_path = os.path.join(
        app.root_path,
        'data',
        str(current_user.id) + ".dat"
    )
    if not os.path.exists(face_encoding_path):
        setup_face = True

    attendance = Attendance.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", setup_face=setup_face, attendance=attendance)


@app.route('/setup-face', methods=["POST"])
@login_required
def setup_face():
    face_encoding_path = os.path.join(
        app.root_path,
        'data',
        str(current_user.id) + ".dat"
    )
    if 'image' not in request.files:
        flash("No image to setup face recognition", category="danger")
        return redirect(url_for('dashboard'))

    file = request.files['image']
    if file:
        image = face_recognition.load_image_file(file)
        face_encodings = face_recognition.face_encodings(image)

        if len(face_encodings) > 0:
            with open(face_encoding_path, 'wb') as f:
                pickle.dump(face_encodings[0], f)

        flash("Successfully setup face recognition", category="success")
        return redirect(url_for('dashboard'))


@app.route('/create', methods=["GET"])
@login_required
def create():
    t = Attendance()
    t.user = current_user
    db.session.add(t)
    db.session.commit()

    return redirect(url_for('dashboard'))


@app.route('/take_attendance', methods=["GET"])
@login_required
def take_attendance():
    return redirect(url_for('dashboard'))


@app.route('/attendance_download', methods=["GET"])
@login_required
def attendance_download():
    return redirect(url_for('dashboard'))


@app.route('/attendance_delete', methods=["GET"])
@login_required
def attendance_delete():
    try:
        if not request.args.get('id') or request.args.get('id') != "":
            id = int(request.args.get('id'))
        else:
            flash("Internal Server Error", category="danger")
    except:
        flash("Internal Server Error", category="danger")

    t = Attendance.query.get(id)
    db.session.delete(t)
    db.session.commit()

    return redirect(url_for('dashboard'))


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
