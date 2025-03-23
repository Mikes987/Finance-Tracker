from . import auth_bp as bp
from .forms import UserLoginForm
from financetracker.models import User
from flask import render_template, redirect, url_for, flash
from flask_login import current_user, logout_user, login_user

@bp.route("/login", methods=['GET', 'POST'])
def login():
    form = UserLoginForm()
    if form.validate_on_submit():
        user = User.get_user(username=form.username.data, password=form.password.data)
        if user is None:
            flash('Wrong User Credentials')
            return redirect(url_for('auth.login'))
        flash('Login successful with: ' + str(user))
        login_user(user)
        return redirect(url_for('main.index'))
    return render_template("login.html", form=form)


@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.index'))