
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
database_url = os.environ.get("DATABASE_URL", "sqlite:///elearning.db")

# Render Postgres URLs sometimes start with postgres://
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="student")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    enrollments = db.relationship("Enrollment", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), unique=True, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    instructor = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    enrollments = db.relationship("Enrollment", backref="course", lazy=True, cascade="all, delete-orphan")


class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("user_id", "course_id", name="unique_user_course"),)


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


def seed_courses():
    if Course.query.count() == 0:
        demo_courses = [
            Course(
                code="CSC101",
                title="Introduction to Computer Science",
                description="Learn basic computer science concepts, problem solving, and digital literacy.",
                instructor="Dr. Aline Mukamana",
            ),
            Course(
                code="NET205",
                title="Computer Networks",
                description="Understand IP addressing, routing, switching, and secure network design.",
                instructor="Mr. Eric Nshimiyimana",
            ),
            Course(
                code="CLOUD301",
                title="Cloud Computing Fundamentals",
                description="Study cloud service models, deployment models, virtualization, and web hosting.",
                instructor="Ms. Diane Uwase",
            ),
            Course(
                code="SEC220",
                title="Cybersecurity Basics",
                description="Explore common threats, security controls, authentication, and safe computing practices.",
                instructor="Mr. Patrick Habimana",
            ),
        ]
        db.session.add_all(demo_courses)
        db.session.commit()


@app.route("/")
def home():
    courses = Course.query.order_by(Course.created_at.desc()).all()
    return render_template("home.html", courses=courses, user=current_user())


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        role = request.form.get("role", "student").strip()

        if not full_name or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "danger")
            return redirect(url_for("register"))

        user = User(full_name=full_name, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", user=current_user())


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("login"))

        session["user_id"] = user.id
        flash(f"Welcome, {user.full_name}!", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html", user=current_user())


@app.route("/logout")
def logout():
    session.clear()
    flash("You have logged out successfully.", "success")
    return redirect(url_for("home"))


@app.route("/dashboard")
def dashboard():
    user = current_user()
    if not user:
        flash("Please log in first.", "danger")
        return redirect(url_for("login"))

    enrollments = Enrollment.query.filter_by(user_id=user.id).all()
    enrolled_course_ids = {en.course_id for en in enrollments}
    courses = Course.query.order_by(Course.title.asc()).all()

    return render_template(
        "dashboard.html",
        user=user,
        courses=courses,
        enrolled_course_ids=enrolled_course_ids,
        enrollment_count=len(enrollments),
    )


@app.route("/enroll/<int:course_id>", methods=["POST"])
def enroll(course_id):
    user = current_user()
    if not user:
        flash("Please log in to enroll in a course.", "danger")
        return redirect(url_for("login"))

    course = Course.query.get_or_404(course_id)

    existing = Enrollment.query.filter_by(user_id=user.id, course_id=course.id).first()
    if existing:
        flash("You are already enrolled in this course.", "warning")
        return redirect(url_for("dashboard"))

    db.session.add(Enrollment(user_id=user.id, course_id=course.id))
    db.session.commit()
    flash(f"You have enrolled in {course.code} - {course.title}.", "success")
    return redirect(url_for("dashboard"))


@app.route("/course/<int:course_id>")
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    user = current_user()
    is_enrolled = False
    if user:
        is_enrolled = Enrollment.query.filter_by(user_id=user.id, course_id=course.id).first() is not None

    return render_template("course_detail.html", course=course, user=user, is_enrolled=is_enrolled)


@app.cli.command("init-db")
def init_db_command():
    db.create_all()
    seed_courses()
    print("Database initialized and demo courses added.")


with app.app_context():
    db.create_all()
    seed_courses()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
