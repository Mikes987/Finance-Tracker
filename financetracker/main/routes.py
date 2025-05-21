from financetracker.main import main_bp as bp
from financetracker.models import View, CurrencyExchanges, MainTypes, Category, Tracking
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from .forms import CreateViewForm, CreateCategoryForm, TrackingForm
import numpy as np
import pandas as pd
from datetime import date, datetime
import financetracker.main.tracking_calculations as tc
from .plotly_graphs import create_date_chart


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    tracking_data = current_user.get_my_tracking_data()
    if not tracking_data.empty:
        currency_symbol = tc.get_current_currency_symbol()
        current_view = View.get_current_view()
        tracking_data_for_graph = tc.create_balance_and_savings_table(tracking_data[tracking_data['view_id']==current_view], current_view)[0]
        # tracking_data_for_graph = tc.create_balance_and_savings_table(tracking_data)
        date_chart = create_date_chart(tracking_data_for_graph, currency_symbol)
        # tc.initiate_dashboard_tables_and_summaries(tracking_data, current_view)
        # all_years, all_months, incomes, expenses, savings, savings_until, recent_month, recent_year = tc.create_dashboard_table_summaries_by_year_month(tracking_data)
        all_years, all_months, incomes, expenses, savings, savings_until, recent_month, recent_year, total_savings = tc.initiate_dashboard_tables_and_summaries(tracking_data, current_view)
    else:
        savings = []
        tracking_data = tracking_data.values
        date_chart = []
        all_years = np.array([])
        all_months = []
        incomes = pd.DataFrame()
        expenses = pd.DataFrame()
        savings = pd.DataFrame()
        savings_until = pd.DataFrame()
        recent_month = None
        recent_year = None
        currency_symbol = None
    return render_template('index.html', title='Index', date_chart=date_chart, all_years=all_years, all_months=all_months, incomes=incomes.values, expenses=expenses.values, savings=savings.values, savings_until=savings_until.values, recent_month=str(recent_month), recent_year=str(recent_year), currency_symbol=currency_symbol, total_savings=total_savings.values)


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
        maintype = form.type_field.data
        category = form.category_field.data
        source_target = form.goal_field.data
        amount = form.amount_field.data
        comment = form.comment_field.data
        Tracking.create_tracking(entry_date=date_entry, maintype=maintype, category=category, target_source=source_target, amount=amount, comment=comment)
        return redirect(url_for('main.tracking'))
    tracking_data = current_user.get_my_tracking_data()
    currency_symbol = tc.get_current_currency_symbol()
    if not tracking_data.empty:
        # tracking_data, savings = tc.create_balance_and_savings_table(tracking_data)
        tracking_data, savings, full_savings = tc.initiate_balance_and_savings_table(tracking_data)
        print(full_savings)
    else:
        savings = []
        full_savings = []
    return render_template('tracking.html', title="Tracking", form=form, categories=categories, types=types, data=tracking_data.values, savings=savings, currency_symbol=currency_symbol, full_savings=full_savings)

@bp.route("/delete_tracking_entry/<tracking_id>")
@login_required
def delete_tracking(tracking_id):
    tracking_id = int(float(tracking_id))
    Tracking.delete_tracking_entry(tracking_id)
    return redirect(url_for('main.tracking'))