from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import db, User, Clinic, Appointment

admin_bp = Blueprint("admin", __name__, url_prefix="/mobi-panel-888x")

# ---------------- Admin access decorator ----------------
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# ---------------- Dashboard ----------------
@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    return render_template(
        "admin/dashboard.html",
        users_count=User.query.count(),
        clinics_count=Clinic.query.count(),
        appointments_count=Appointment.query.count()
    )

# ---------------- Users Management ----------------
@admin_bp.route("/users")
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    return render_template("admin/users.html", users=users)

@admin_bp.route("/users/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_user():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")  # hash in production
        role = request.form.get("role")  # 'mother' or 'clinic'
        if username and password and role:
            user = User(username=username, password=password, role=role)
            db.session.add(user)
            db.session.commit()
            flash("User added successfully!", "success")
            return redirect(url_for("admin.manage_users"))
        flash("All fields are required", "danger")
    return render_template("admin/add_user.html")

@admin_bp.route("/users/edit/<int:user_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == "POST":
        user.username = request.form.get("username")
        user.role = request.form.get("role")
        db.session.commit()
        flash("User updated!", "success")
        return redirect(url_for("admin.manage_users"))
    return render_template("admin/edit_user.html", user=user)

@admin_bp.route("/users/delete/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted!", "success")
    return redirect(url_for("admin.manage_users"))

# ---------------- Clinics Management ----------------
@admin_bp.route("/clinics")
@login_required
@admin_required
def manage_clinics():
    clinics = Clinic.query.all()
    return render_template("admin/clinics.html", clinics=clinics)

@admin_bp.route("/clinics/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_clinic():
    if request.method == "POST":
        name = request.form.get("name")
        address = request.form.get("address")
        phone = request.form.get("phone")
        if name and address and phone:
            clinic = Clinic(name=name, address=address, phone=phone)
            db.session.add(clinic)
            db.session.commit()
            flash("Clinic added successfully!", "success")
            return redirect(url_for("admin.manage_clinics"))
        flash("All fields are required", "danger")
    return render_template("admin/add_clinic.html")

@admin_bp.route("/clinics/edit/<int:clinic_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_clinic(clinic_id):
    clinic = Clinic.query.get_or_404(clinic_id)
    if request.method == "POST":
        clinic.name = request.form.get("name")
        clinic.address = request.form.get("address")
        clinic.phone = request.form.get("phone")
        db.session.commit()
        flash("Clinic updated!", "success")
        return redirect(url_for("admin.manage_clinics"))
    return render_template("admin/edit_clinic.html", clinic=clinic)

@admin_bp.route("/clinics/delete/<int:clinic_id>", methods=["POST"])
@login_required
@admin_required
def delete_clinic(clinic_id):
    clinic = Clinic.query.get_or_404(clinic_id)
    db.session.delete(clinic)
    db.session.commit()
    flash("Clinic deleted!", "success")
    return redirect(url_for("admin.manage_clinics"))

# ---------------- Appointments Management ----------------
@admin_bp.route("/appointments")
@login_required
@admin_required
def manage_appointments():
    clinic_filter = request.args.get("clinic")
    date_filter = request.args.get("date")
    query = Appointment.query.order_by(Appointment.date.desc())
    
    if clinic_filter:
        query = query.filter_by(clinic=clinic_filter)
    if date_filter:
        query = query.filter_by(date=date_filter)
    
    appointments = query.all()
    clinics = [c.name for c in Clinic.query.all()]  # for filter dropdown
    return render_template(
        "admin/appointments.html",
        appointments=appointments,
        clinics=clinics,
        selected_clinic=clinic_filter,
        selected_date=date_filter
    )

@admin_bp.route("/appointments/edit/<int:appointment_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    clinics = Clinic.query.all()
    if request.method == "POST":
        appointment.mother_name = request.form.get("mother_name")
        appointment.phone = request.form.get("phone")
        appointment.clinic = request.form.get("clinic")
        appointment.date = request.form.get("date")
        appointment.notes = request.form.get("notes")
        db.session.commit()
        flash("Appointment updated!", "success")
        return redirect(url_for("admin.manage_appointments"))
    return render_template("admin/edit_appointment.html", appointment=appointment, clinics=clinics)

@admin_bp.route("/appointments/delete/<int:appointment_id>", methods=["POST"])
@login_required
@admin_required
def delete_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    db.session.delete(appointment)
    db.session.commit()
    flash("Appointment deleted!", "success")
    return redirect(url_for("admin.manage_appointments"))
