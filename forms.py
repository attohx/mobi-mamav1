from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")

class TipForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=200)])
    content = TextAreaField("Content", validators=[DataRequired()])
    language = SelectField("Language", choices=[('en','English'), ('tw','Twi')])
    audio_filename = StringField("Audio Filename (place file in static/audio/)", validators=[])
    submit = SubmitField("Save Tip")

class AppointmentForm(FlaskForm):
    mother_name = StringField("Your name", validators=[DataRequired()])
    phone = StringField("Phone number", validators=[DataRequired()])
    clinic = StringField("Preferred clinic", validators=[DataRequired()])
    date = StringField("Preferred date/time", validators=[DataRequired()])
    notes = TextAreaField("Notes (optional)")
    submit = SubmitField("Book Appointment")
