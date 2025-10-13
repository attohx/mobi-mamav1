from flask import render_template, redirect, url_for, flash, Blueprint 
from flask_login import login_required, current_user
from models import db, Tip, Appointment
from forms import TipForm, AppointmentForm

#initialize clinic route
clinic_bp = Blueprint("clinic", __name__)

@clinic_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role != "clinic":
        flash("Access denied.", "danger")
        return redirect(url_for("main.index"))

    tips = Tip.query.order_by(Tip.created_at.desc()).all()
    appts = Appointment.query.order_by(Appointment.created_at.desc()).all()
    return render_template("clinic_dashboard.html", tips=tips, appts=appts)


@clinic_bp.route("/add_tip", methods=["GET", "POST"])
@login_required
def add_tip():
    if current_user.role != "clinic":
        flash("Access denied.", "danger")
        return redirect(url_for("main.index"))

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
        return redirect(url_for("clinic.dashboard"))
    return render_template("add_tip.html", form=form)


@clinic_bp.route("/edit_tip/<int:tip_id>", methods=["GET", "POST"])
@login_required
def edit_tip(tip_id):
    if current_user.role != "clinic":
        flash("Access denied.", "danger")
        return redirect(url_for("main.index"))

    tip = Tip.query.get_or_404(tip_id)
    form = TipForm(obj=tip)
    if form.validate_on_submit():
        tip.title = form.title.data
        tip.content = form.content.data
        tip.language = form.language.data
        tip.audio_filename = form.audio_filename.data or None
        db.session.commit()
        flash("Tip updated successfully!", "success")
        return redirect(url_for("clinic.dashboard"))
    return render_template("add_tip.html", form=form, edit=True)


@clinic_bp.route("/delete_tip/<int:tip_id>")
@login_required
def delete_tip(tip_id):
    if current_user.role != "clinic":
        flash("Access denied.", "danger")
        return redirect(url_for("main.index"))

    tip = Tip.query.get_or_404(tip_id)
    db.session.delete(tip)
    db.session.commit()
    flash("Tip deleted successfully.", "success")
    return redirect(url_for("clinic.dashboard"))


@clinic_bp.route("/edit_appointment/<int:appt_id>", methods=["GET", "POST"])
@login_required
def edit_appointment(appt_id):
    if current_user.role != "clinic":
        flash("Access denied.", "danger")
        return redirect(url_for("main.index"))

    appt = Appointment.query.get_or_404(appt_id)
    form = AppointmentForm(obj=appt)
    if form.validate_on_submit():
        appt.mother_name = form.mother_name.data
        appt.phone = form.phone.data
        appt.clinic = form.clinic.data
        appt.date = form.date.data
        appt.notes = form.notes.data
        db.session.commit()
        flash("Appointment updated successfully!", "success")
        return redirect(url_for("clinic.dashboard"))
    return render_template("appointments.html", form=form, edit=True)
