from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user
from models import User
from forms import AdminLoginForm

admin_auth_bp = Blueprint("admin_auth", __name__, url_prefix="/mobi-panel-888x")

@admin_auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = AdminLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data, role='admin').first()
        if user and user.password == form.password.data:  # hash in production
            login_user(user)
            flash("Welcome to Mobi Panel!", "success")
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.dashboard'))
        flash("Invalid admin credentials", "danger")
    return render_template("admin/login.html", form=form)
