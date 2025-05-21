from . import auth_bp as bp
from .forms import UserLoginForm, RegistrationForm, MailToResetPassword, ResetPasswordForm
from financetracker import db
from financetracker.models import User, MainTypes, CurrencyUpdateStatus
from financetracker.email import request_new_password_mail
from flask import render_template, redirect, url_for, flash
from flask_login import logout_user, login_user, current_user, login_required


@bp.route("/login", methods=['GET', 'POST'])
def login():
    form = UserLoginForm()
    if form.validate_on_submit():
        user = User.get_user(username=form.username.data, password=form.password.data)
        if user is None:
            flash('Wrong User Credentials')
            return redirect(url_for('auth.login'))
        login_user(user)
        
        # Here for updating currency exchange rates
        CurrencyUpdateStatus.update_currency_exchanges()
        return redirect(url_for('main.index'))
    return render_template("login.html", form=form, title='Login')


@bp.route("/logout")
@login_required
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
        
        # Function for 3 Main types
        MainTypes.check_for_initial_types()
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Register', form=form)


@bp.route('/forgotpassword', methods=['GET', 'POST'])
def click_password_reset():
    form = MailToResetPassword()
    if form.validate_on_submit():
        user = User.get_user_by_mail(form.email.data)
        request_new_password_mail(user)
        if not user:
            flash("email doesn't exist.")
            return redirect(url_for('auth.click_password_reset'))
        return redirect(url_for('auth.login'))
    return render_template("mailforpasswordreset.html", title='E Mail for Password Reset', form=form)


@bp.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.verify_token(token)
        if user is None:
            flash("User doesn't exist")
            return redirect(url_for('main.index'))
        user.create_password(form.password1.data)
        db.session.add(user)
        db.session.commit()
        flash('Password successfully changed.')
        return redirect(url_for('auth.login'))
    return render_template("reset_password_form.html", title="Reset Password", form=form)