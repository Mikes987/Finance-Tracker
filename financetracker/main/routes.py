from financetracker.main import main_bp as bp
from flask import render_template
from flask_login import current_user


@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html', title='Index')