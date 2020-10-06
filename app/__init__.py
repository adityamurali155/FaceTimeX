from flask import Flask, render_template, flash, request, redirect, url_for, send_file, make_response
from flask_login import current_user, LoginManager, login_user, logout_user, login_required
from flask_qrcode import QRcode
import flask_excel as excel
import pyexcel
import face_recognition
import numpy as np
from datetime import datetime

from app.config import Config
from app.models import db, bcrypt, User, Candidate, Attendance, Record
from app.oauth import github_blueprint, google_blueprint

app = Flask(__name__)
app.config.from_object(Config)
bcrypt.init_app(app)
db.init_app(app)
qrcode = QRcode(app)
excel.init_excel(app)

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


@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    tab = "records"

    if "tab" in request.args and request.args["tab"] in ["records", "attendance", "candidates"]:
        tab = request.args["tab"]

    page = request.args.get('page', 1, type=int)

    if tab == "attendance":
        list = Attendance.query
        .filter_by(user=current_user)
        .order_by(
            Attendance.created_at.desc()
        ).paginate(
            page, 10, error_out=False
        )
    elif tab == "candidates":
        list = Candidate.query
        .filter_by(user=current_user)
        .order_by(
            Candidate.last_attendance.desc()
        ).paginate(
            page, 10, error_out=False
        )
    else:
        list = Record.query.order_by(
            Record.created_at.desc()
        ).paginate(
            page, 10, error_out=False
        )

    return render_template(
        "dashboard.html",
        tab=tab,
        list=list
    )


@app.route("/new_attendance", methods=["POST"])
@login_required
def new_attendance():
    t = Attendance()

    t.description = request.form["description"]
    t.user = current_user

    db.session.add(t)
    db.session.commit()

    return redirect(url_for("dashboard", tab="attendance"))


@app.route("/delete_record", methods=["POST"])
@login_required
def delete_record():
    id = request.form.get("id", type=int)
    record = Record.query.get(id)
    if record:
        db.session.delete(record)
        db.session.commit()
    return redirect(url_for("dashboard", tab="records"))


@app.route("/delete_attendance", methods=["POST"])
@login_required
def delete_attendance():
    id = request.form.get("id", type=int)
    attendance = Attendance.query.get(id)
    if attendance:
        db.session.delete(attendance)
        db.session.commit()
    return redirect(url_for("dashboard", tab="attendance"))


@app.route("/delete_candidate", methods=["POST"])
@login_required
def delete_candidate():
    id = request.form.get("id", type=int)
    candidate = Candidate.query.get(id)
    if candidate:
        db.session.delete(candidate)
        db.session.commit()
    return redirect(url_for("dashboard", tab="candidates"))


@app.route("/download_attendance", methods=["POST"])
@login_required
def download_attendance():
    id = request.form.get("id", type=int)
    attendance = Attendance.query.get(id)
    if attendance:
        sheet = []
        sheet.append(["Sno", "Name", "Time"])
        records = Record.query.filter_by(attendance=attendance).all()
        print(records)
        for i in range(len(records)):
            t = records[i]
            sheet.append([
                i + 1,
                t.candidate.name,
                t.created_at.strftime('%I:%M %p %d %B, %Y')
            ])

        print(sheet)
        return excel.make_response_from_array(sheet, "xls", file_name="Attendance_" + str(attendance.created_at))

    return redirect(url_for("dashboard", tab="attendance"))


@app.route("/new_candidate/<int:id>", methods=["GET", "POST"])
def new_candidate(id):

    if request.method == "POST":
        if not "image" in request.files:
            return "no image found", 400

        file = request.files["image"]

        if not file:
            return "no image found", 400

        image = face_recognition.load_image_file(file)
        encodings = face_recognition.face_encodings(image)

        if(len(encodings) != 1):
            return str(len(encodings)) + " faces found. But required only 1 face", 400

        user = User.query.get(id)
        if not user:
            return "invalid user", 400

        candidate = Candidate()

        candidate.name = request.form.get("name", type=str)
        candidate.encoding = encodings[0]
        candidate.user = user

        db.session.add(candidate)
        db.session.commit()

        return "created", 201

    return render_template("new_candidate.html", id=id)


@app.route("/take_attendance/<int:id>", methods=["GET", "POST"])
def take_attendance(id):

    if request.method == "POST":
        if not "image" in request.files:
            return "no image found", 400

        file = request.files["image"]

        if not file:
            return "no image found", 400

        image = face_recognition.load_image_file(file)
        encodings = face_recognition.face_encodings(image)

        if(len(encodings) != 1):
            return str(len(encodings)) + " faces found. But required only 1 face", 400

        attendance = Attendance.query.get(id)
        if not attendance:
            return "invalid attendance id", 400

        # logic
        candidates = Candidate.query.filter_by(user=attendance.user).all()
        known_encodings = []
        for c in candidates:
            known_encodings.append(c.encoding)

        result = face_recognition.compare_faces(known_encodings, encodings[0])

        for i in range(len(result)):
            if result[i]:
                if Record.query.filter_by(candidate=candidates[i], attendance=attendance).first() is not None:
                    return "success", 200

                record = Record()

                now = datetime.now()
                record.candidate = candidates[i]
                record.attendance = attendance
                record.created_at = now
                record.candidate.last_attendance = now

                db.session.add_all([record, record.candidate])
                db.session.commit()

                return "success", 200

        return "unauthorized", 401

    return render_template("take_attendance.html", id=id)
