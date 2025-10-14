from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo


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

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    role = SelectField('Role', choices=[('mother', 'Mother'), ('clinic', 'Clinic')], validators=[DataRequired()])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class AdminLoginForm(FlaskForm):
    username = StringField('Admin Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')