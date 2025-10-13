from dotenv import load_dotenv
import os
from flask import render_template, redirect, url_for, flash, request, session, Blueprint
from flask_login import login_required, current_user
from models import Appointment, Tip, db
from forms import AppointmentForm
import google.generativeai as genai
from openai import OpenAI

# Load environment variables
load_dotenv()

# ✅ Configure AI clients
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize mother blueprint
mother_bp = Blueprint("mother", __name__)


# ------------------- MOTHER DASHBOARD -------------------
@mother_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role != "mother":
        flash("Access denied.", "danger")
        return redirect(url_for("main.index"))

    appointments = Appointment.query.filter_by(
        mother_name=current_user.username
    ).order_by(Appointment.created_at.desc()).all()

    tips = Tip.query.order_by(Tip.created_at.desc()).limit(5).all()

    return render_template("user_dashboard.html", appointments=appointments, tips=tips)


# ------------------- APPOINTMENTS -------------------
@mother_bp.route("/appointments", methods=["GET", "POST"])
@login_required
def appointments():
    if current_user.role != "mother":
        flash("Access denied.", "danger")
        return redirect(url_for("main.index"))

    form = AppointmentForm()

    if form.validate_on_submit():
        appt = Appointment(
            mother_name=current_user.username,
            phone=form.phone.data,
            clinic=form.clinic.data,
            date=form.date.data,
            notes=form.notes.data,
        )
        db.session.add(appt)
        db.session.commit()
        flash("Appointment booked successfully!", "success")
        return redirect(url_for("mother.appointments"))

    appointments = Appointment.query.filter_by(
        mother_name=current_user.username
    ).order_by(Appointment.created_at.desc()).all()

    return render_template("appointments.html", form=form, appts=appointments)


# ------------------- ASK MOBI (AI Chatbot) -------------------
@mother_bp.route("/ask_mobi", methods=["GET", "POST"])
@login_required
def ask_mobi():
    if current_user.role != "mother":
        flash("Access denied — only mothers can use Ask Mobi.", "danger")
        return redirect(url_for("main.index"))

    response_text = None
    user_message = None

    if request.method == "POST":
        user_message = request.form.get("message")
        if user_message:
            lang = session.get("lang", "en")
            system_prompt = (
                "You are Mobi, a friendly maternal health assistant for mothers in Ghana. "
                "Respond kindly, clearly, and accurately. If asked for a diagnosis, "
                "advise visiting a health center. Respond in "
                f"{'Twi' if lang == 'tw' else 'English'}."
            )

            # Choose Gemini or OpenAI
            use_gemini = True

            try:
                if use_gemini:
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    chat = model.start_chat(history=[])
                    response = chat.send_message(f"{system_prompt}\nUser: {user_message}")
                    response_text = response.text
                else:
                    completion = openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_message},
                        ],
                        temperature=0.7,
                    )
                    response_text = completion.choices[0].message.content

            except Exception as e:
                print("AI Error:", e)
                response_text = "Sorry, Mobi is currently unavailable. Please try again later."

    return render_template("ask_mobi.html", response=response_text, user_message=user_message)
