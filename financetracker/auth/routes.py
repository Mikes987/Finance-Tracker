from . import auth_bp as bp
from .forms import UserLoginForm, RegistrationForm
#from financetracker import db
from financetracker.models import User
from flask import render_template, redirect, url_for, flash
from flask_login import logout_user, login_user
#from werkzeug.security import generate_password_hash

@bp.route("/login", methods=['GET', 'POST'])
def login():
    form = UserLoginForm()
    if form.validate_on_submit():
        user = User.get_user(username=form.username.data, password=form.password.data)
        if user is None:
            flash('Wrong User Credentials')
            return redirect(url_for('auth.login'))
        login_user(user)
        return redirect(url_for('main.index'))
    return render_template("login.html", form=form, title='Login')


@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        User.create_user(username=form.username.data,
                         password=form.password.data,
                         email=form.email.data)
        flash('User successfully created.')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Register', form=form)