from financetracker.main import main_bp as bp
from flask import render_template


@bp.route('/')
@bp.route('/index')
def first():
    user = {'name': 'Michael'}
    return render_template('index.html', user=user, title='Index')