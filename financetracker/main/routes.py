from financetracker.main import main_bp as bp
from financetracker.models import View, CurrencyExchanges, MainTypes, Category, Tracking
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from .forms import CreateViewForm, CreateCategoryForm, TrackingForm
import numpy as np
from datetime import date, datetime


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    return render_template('index.html', title='Index')


@bp.route("/user/<username>")
@login_required
def usersettings(username: str):
    if current_user.username != username:
        flash("You're not allowed to enter that page.")
        return redirect(url_for('main.index'))
    number_of_views = View.get_number_of_views(current_user.id)
    view_settings = View.get_views_in_table(current_user.id)
    if number_of_views != 0:
        arr = np.array(view_settings)
        idx = arr[arr[:, 2]=='True'][0, 0]
        user_categories = Category.get_all_categories(int(idx))
    else:
        idx = 0
        user_categories = None
    return render_template('usersettings.html', title="User Settings", val=number_of_views, table_content=view_settings, idx=idx, user_categories=user_categories)


@bp.route("/create_view", methods=['GET', 'POST'])
@login_required
def create_view():
    form = CreateViewForm()
    if request.method == 'GET':
        form.currency.choices = CurrencyExchanges.get_all_currencies()
        return render_template('create_view.html', title="Create View", form=form)
    elif request.method == 'POST':
        View.create_view(form.currency.data)
        return redirect(url_for('main.usersettings', username=current_user.username))


@bp.route("/change_view/<int:view_id>")
@login_required
def change_view(view_id):
    View.change_view(view_id)
    return redirect(url_for('main.usersettings', username=current_user.username))


@bp.route("/create_category/<view_id>", methods=['GET', 'POST'])
@login_required
def create_category(view_id):
    form = CreateCategoryForm()
    choices = MainTypes.get_all_types()
    form.type_field.choices = choices
    if form.validate_on_submit():
        Category.create_category(category=form.category_field.data, main_type_string=form.type_field.data, view_id=view_id)
        return redirect(url_for('main.usersettings', username=current_user.username))
    return render_template('create_category.html', title='Create Category', form=form)

@bp.route("/tracking", methods=['GET', 'POST'])
@login_required
def tracking():
    form = TrackingForm()
    types = MainTypes.get_all_types()
    current_view = View.get_current_view()
    categories = Category.get_all_categories(current_view)
    form.type_field.choices = types
    form.category_field.choices = categories[0]
    form.goal_field.choices = categories[2]
    if form.validate_on_submit():
        date_entry = form.date_field.data
        date_entry = datetime.strptime(date_entry, '%Y-%m-%d').date()
        maintype = form.type_field.data
        category = form.category_field.data
        source_target = form.goal_field.data
        amount = float(form.amount_field.data)
        comment = form.comment_field.data
        Tracking.create_tracking(entry_date=date_entry, maintype=maintype, category=category, target_source=source_target, amount=amount, comment=comment)
        return redirect(url_for('main.tracking'))
    tracking_data = Tracking.get_all_tracking_data_by_user_and_view()
    return render_template('tracking.html', title="Tracking", form=form, categories=categories, types=types, data=tracking_data)