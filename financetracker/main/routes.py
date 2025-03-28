from financetracker.main import main_bp as bp
from flask import render_template, redirect, url_for
from flask_login import current_user


@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html', title='Index')


@bp.route("/user/<username>")
def usersettings(username: str):
    if current_user.is_anonymous:
        print("No redirect!")
        return redirect(url_for('main.index'))
    return render_template('usersettings.html', title="User Settings")