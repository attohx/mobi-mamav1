import os
from flask import Flask, render_template, redirect, url_for, flash, request, send_from_directory
from config import Config
from models import db, User, Tip, Appointment
from forms import LoginForm, TipForm, AppointmentForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from pathlib import Path

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ensure instance and upload folders exist
    Path(os.path.join(app.root_path, 'instance')).mkdir(parents=True, exist_ok=True)
    Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)

    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ✅ Initialize database + seed default data right away
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username="nurse").first():
            nurse = User(
                username="nurse",
                password=generate_password_hash("password"),
                role="nurse"
            )
            db.session.add(nurse)
            db.session.commit()
        if Tip.query.count() == 0:
            t = Tip(
                title="Early prenatal visits",
                content="Visit your clinic early in pregnancy for check-ups and tests.",
                language="en",
                audio_filename="example_en.mp3"
            )
            db.session.add(t)
            db.session.commit()

    # ------------------- ROUTES -------------------

    @app.route("/")
    def index():
        lang = request.args.get('lang', 'en')
        tips = Tip.query.filter_by(language=lang).order_by(Tip.created_at.desc()).all()
        return render_template("index.html", tips=tips, lang=lang)

    @app.route("/tip/<int:tip_id>")
    def tip_detail(tip_id):
        tip = Tip.query.get_or_404(tip_id)
        return render_template("tip.html", tip=tip)

    @app.route("/appointments", methods=["GET", "POST"])
    def appointments():
        form = AppointmentForm()
        if form.validate_on_submit():
            appt = Appointment(
                mother_name=form.mother_name.data,
                phone=form.phone.data,
                clinic=form.clinic.data,
                date=form.date.data,
                notes=form.notes.data
            )
            db.session.add(appt)
            db.session.commit()
            flash("Appointment requested — nurse will contact you.", "success")
            return redirect(url_for("appointments"))
        appts = Appointment.query.order_by(Appointment.created_at.desc()).all() if current_user.is_authenticated and current_user.role == 'nurse' else None
        return render_template("appointments.html", form=form, appts=appts)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("nurse_dashboard"))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("Logged in", "success")
                return redirect(url_for("nurse_dashboard"))
            flash("Invalid credentials", "danger")
        return render_template("login.html", form=form)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("Logged out", "info")
        return redirect(url_for("index"))

    @app.route("/nurse/dashboard")
    @login_required
    def nurse_dashboard():
        if current_user.role != 'nurse':
            flash("Access denied", "danger")
            return redirect(url_for("index"))
        tips = Tip.query.order_by(Tip.created_at.desc()).all()
        appts = Appointment.query.order_by(Appointment.created_at.desc()).all()
        return render_template("nurse_dashboard.html", tips=tips, appts=appts)

    @app.route("/nurse/add_tip", methods=["GET", "POST"])
    @login_required
    def add_tip():
        if current_user.role != 'nurse':
            flash("Access denied", "danger")
            return redirect(url_for("index"))
        form = TipForm()
        if form.validate_on_submit():
            tip = Tip(
                title=form.title.data,
                content=form.content.data,
                language=form.language.data,
                audio_filename=form.audio_filename.data or None
            )
            db.session.add(tip)
            db.session.commit()
            flash("Tip added", "success")
            return redirect(url_for("nurse_dashboard"))
        return render_template("add_tip.html", form=form)

    # Serve audio files (static will also serve them)
    @app.route('/audio/<filename>')
    def audio_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
