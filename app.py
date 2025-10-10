import os
from flask import Flask, render_template, redirect, url_for, flash, request, send_from_directory, session, g
from config import Config
from models import db, User, Tip, Appointment
from forms import LoginForm, TipForm, AppointmentForm, RegisterForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from pathlib import Path


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure instance and upload folders exist
    Path(os.path.join(app.root_path, "instance")).mkdir(parents=True, exist_ok=True)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ✅ Initialize database + seed default nurse + tips
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(username="nurse").first():
            nurse = User(
                username="nurse",
                password=generate_password_hash("password"),
                role="nurse",
            )
            db.session.add(nurse)
            db.session.commit()

        if Tip.query.count() == 0:
            english_tips = [
                Tip(
                    title="Early Prenatal Visits",
                    content="Visit your clinic early in pregnancy for check-ups and tests. Early visits help detect and prevent complications.",
                    language="en",
                ),
                Tip(
                    title="Balanced Diet During Pregnancy",
                    content="Eat a variety of foods including fruits, vegetables, and proteins. Avoid alcohol and limit sugary or processed foods.",
                    language="en",
                ),
                Tip(
                    title="Stay Hydrated",
                    content="Drink enough clean water daily to stay healthy. Dehydration can cause fatigue and other health problems during pregnancy.",
                    language="en",
                ),
                Tip(
                    title="Regular Exercise",
                    content="Engage in light physical activities like walking to keep your body fit and improve blood circulation.",
                    language="en",
                ),
                Tip(
                    title="Newborn Hygiene",
                    content="Keep your baby’s environment clean, wash hands before touching your baby, and ensure clean feeding bottles and cloths.",
                    language="en",
                ),
            ]

            twi_tips = [
                Tip(
                    title="Apɔw Mmere A Ɛyɛ Fɛ",
                    content="Kɔ adwumayɛbea no ntɛm na yɛ nhwehwɛmu. Sɛ wokɔ ntɛm a, ɛboa ma wɔhu nsɛm a ɛbɛyɛ adwuma ama wo ne abɔfra no.",
                    language="tw",
                ),
                Tip(
                    title="Nnuane Pa A Ɛsɔ Wo Ho",
                    content="Di nnuane a ɛwɔ abɔdeɛ, dua, ne abɔdwe. Gyae nsã ne nnuane a wɔde suga ne aduan a ɛyɛ sɛ ahuhoɔ.",
                    language="tw",
                ),
                Tip(
                    title="Nom Nsuo Fɛfɛɛfɛ",
                    content="Nom nsuo pa daa. Sɛ nsuo no ho tew a, ɛboa ma wotena den na ɛbɔ wo ho ban fi ho yareɛ.",
                    language="tw",
                ),
                Tip(
                    title="Ɛyɛ Adwuma Kakra",
                    content="Yɛ adwuma kakra te sɛ anammɔn kɔkɔɔ. Ɛboa ma mogya kɔɔ no yɛ papa na w’ahome hyɛ den.",
                    language="tw",
                ),
                Tip(
                    title="Hwɛ Abɔfra No Ho Fɛfɛɛfɛ",
                    content="Fa wo nsam ho yie ansa na wafa abɔfra no. Ma ne ho tew na di nsuo a ɛho tew nko ara.",
                    language="tw",
                ),
            ]

            db.session.bulk_save_objects(english_tips + twi_tips)
            db.session.commit()
            print("✅ Sample English & Twi tips added.")

    # ------------------- LANGUAGE SUPPORT -------------------

    @app.before_request
    def set_language():
        lang = request.args.get("lang")
        if lang:
            session["lang"] = lang
        g.lang = session.get("lang", "en")

    @app.context_processor
    def inject_translations():
        translations = {
            "en": {
                "title": "Health Tips",
                "switch_to": "Switch language",
                "book": "Book an Appointment",
                "read_more": "Read More",
                "welcome": "Welcome to Mobi Mama",
                "subtitle": "Empowering mothers with healthcare guidance and education.",
                "login": "Login",
                "signup": "Sign Up",
            },
            "tw": {
                "title": "Apɔw Mu Nkyerɛkyerɛ",
                "switch_to": "Sesa kasa",
                "book": "Paw Appɔintment",
                "read_more": "Kenkan Bio",
                "welcome": "Akwaaba Mobi Mama",
                "subtitle": "Yɛboa maamefoɔ wɔ Ghana anaafoɔ sɛ wɔnya apɔw ho nkyerɛkyerɛ ne abotare.",
                "login": "Kɔ Mu",
                "signup": "Bɔ Akawnt",
            },
        }
        return {"t": translations[g.lang], "current_lang": g.lang}

    # ------------------- ROUTES -------------------

    @app.route("/")
    def index():
        lang = g.lang
        tips = Tip.query.filter_by(language=lang).order_by(Tip.created_at.desc()).all()
        return render_template("index.html", tips=tips, lang=lang)

    # Mother Registration
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for("index"))

        form = RegisterForm()
        if form.validate_on_submit():
            if User.query.filter_by(username=form.username.data).first():
                flash("Username already exists.", "warning")
            else:
                user = User(
                    username=form.username.data,
                    password=generate_password_hash(form.password.data),
                    role="mother",
                )
                db.session.add(user)
                db.session.commit()
                flash("Account created successfully! Please log in.", "success")
                return redirect(url_for("login"))
        return render_template("register.html", form=form)

    # Login for both nurse & mother
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            if current_user.role == "nurse":
                return redirect(url_for("nurse_dashboard"))
            return redirect(url_for("index"))

        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and check_password_hash(user.password, form.password.data):
                login_user(user)
                flash(f"Welcome back, {user.username}!", "success")
                if user.role == "nurse":
                    return redirect(url_for("nurse_dashboard"))
                else:
                    return redirect(url_for("index"))
            flash("Invalid username or password", "danger")
        return render_template("login.html", form=form)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("You’ve been logged out.", "info")
        return redirect(url_for("index"))

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
                notes=form.notes.data,
            )
            db.session.add(appt)
            db.session.commit()
            flash("Appointment request sent successfully!", "success")
            return redirect(url_for("appointments"))
        appts = (
            Appointment.query.order_by(Appointment.created_at.desc()).all()
            if current_user.is_authenticated and current_user.role == "nurse"
            else None
        )
        return render_template("appointments.html", form=form, appts=appts)

    @app.route("/nurse/dashboard")
    @login_required
    def nurse_dashboard():
        if current_user.role != "nurse":
            flash("Access denied.", "danger")
            return redirect(url_for("index"))
        tips = Tip.query.order_by(Tip.created_at.desc()).all()
        appts = Appointment.query.order_by(Appointment.created_at.desc()).all()
        return render_template("nurse_dashboard.html", tips=tips, appts=appts)

    @app.route("/nurse/add_tip", methods=["GET", "POST"])
    @login_required
    def add_tip():
        if current_user.role != "nurse":
            flash("Access denied.", "danger")
            return redirect(url_for("index"))
        form = TipForm()
        if form.validate_on_submit():
            tip = Tip(
                title=form.title.data,
                content=form.content.data,
                language=form.language.data,
                audio_filename=form.audio_filename.data or None,
            )
            db.session.add(tip)
            db.session.commit()
            flash("Tip added successfully!", "success")
            return redirect(url_for("nurse_dashboard"))
        return render_template("add_tip.html", form=form)

    @app.route("/audio/<filename>")
    def audio_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)
    
    # ------------------- EDIT TIP -------------------
    @app.route("/nurse/edit_tip/<int:tip_id>", methods=["GET", "POST"])
    @login_required
    def edit_tip(tip_id):
        if current_user.role != "nurse":
            flash("Access denied.", "danger")
            return redirect(url_for("index"))

        tip = Tip.query.get_or_404(tip_id)
        form = TipForm(obj=tip)
        if form.validate_on_submit():
            tip.title = form.title.data
            tip.content = form.content.data
            tip.language = form.language.data
            tip.audio_filename = form.audio_filename.data or None
            db.session.commit()
            flash("Tip updated successfully!", "success")
            return redirect(url_for("nurse_dashboard"))
        return render_template("add_tip.html", form=form, edit=True)


    # ------------------- DELETE TIP -------------------
    @app.route("/nurse/delete_tip/<int:tip_id>")
    @login_required
    def delete_tip(tip_id):
        if current_user.role != "nurse":
            flash("Access denied.", "danger")
            return redirect(url_for("index"))

        tip = Tip.query.get_or_404(tip_id)
        db.session.delete(tip)
        db.session.commit()
        flash("Tip deleted successfully.", "success")
        return redirect(url_for("nurse_dashboard"))


    # ------------------- EDIT APPOINTMENT -------------------
    @app.route("/nurse/edit_appointment/<int:appt_id>", methods=["GET", "POST"])
    @login_required
    def edit_appointment(appt_id):
        if current_user.role != "nurse":
            flash("Access denied.", "danger")
            return redirect(url_for("index"))

        appt = Appointment.query.get_or_404(appt_id)
        form = AppointmentForm(obj=appt)
        if form.validate_on_submit():
            appt.mother_name = form.mother_name.data
            appt.phone = form.phone.data
            appt.clinic = form.clinic.data
            appt.date = form.date.data
            appt.notes = form.notes.data
            appt.status = form.status.data
            db.session.commit()
            flash("Appointment updated successfully!", "success")
            return redirect(url_for("nurse_dashboard"))
        return render_template("appointments.html", form=form, edit=True)


        return app


if __name__ == "__main__":
    import os
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
