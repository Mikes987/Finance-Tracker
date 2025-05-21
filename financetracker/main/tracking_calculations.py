from decimal import Decimal
import pandas as pd
import numpy as np
from financetracker.models import CurrencyExchanges
from babel.numbers import get_currency_symbol
from flask_login import current_user

def get_current_currency_symbol():
    current_currency_code = CurrencyExchanges.get_current_currency()
    current_currency_symbol = get_currency_symbol(current_currency_code)
    return current_currency_symbol

def create_balance_and_savings_table(df: pd.DataFrame, current_view):
    view = df['view_id'].unique()[0]
    savings = df[df['type']=='Savings']
    saving_arr = [df]
    for index, row in savings.iterrows():
        df_single = pd.DataFrame({'date': [row['date'], row['date']], 'type': ['Income', 'Expenses'], 'amount': [row['amount'], row['amount']], "Source/Target": [row['category'], row['Source/Target']]})
        saving_arr.append(df_single)

    df = pd.concat(saving_arr)
    del saving_arr
    
    df['sign'] = np.where(df['type']=='Income', 1, np.where(df['type']=='Expenses', -1, 0))
    df['curr'] = df['sign'] * df['amount']
    
    df_savings = df.groupby(df['Source/Target']).agg(Savings=('curr', 'sum')).reset_index().rename(columns={'Source/Target': 'Category'})
    df_savings = pd.concat([df_savings, pd.DataFrame({'Category': ['Total'], 'Savings': [sum(df_savings['Savings'])]})], ignore_index=True)
    
    df.dropna(inplace=True)
    
    if view == current_view:
        df_sums = df.groupby(df['date']).agg(Curr=('curr', 'sum')).reset_index().sort_values(by=['date'])
        df_sums['Balance'] = df_sums['Curr'].cumsum()
        df_sums['Balance'] = df_sums['Balance'].apply(lambda x: round(x, 2))
        df_sums.drop(columns=['Curr'], inplace=True)
        
        df = df.merge(df_sums).sort_values(by='date', ascending=False)
        del df_sums
        df.drop(columns=['sign', 'curr'], inplace=True)
        df = df.reindex(columns=['date', 'type', 'category', 'amount', 'Source/Target', 'comment', 'Balance', 'id'])
        
        df['date'] = pd.to_datetime(df['date'])
        df['id'] = df['id'].astype('int64')
    
    return df, df_savings.values


def initiate_balance_and_savings_table(df_original: pd.DataFrame):
    current_view = current_user.get_my_current_view()
    df = df_original[df_original['view_id']==current_view]
    result, savings = create_balance_and_savings_table(df, current_view)
    savings_table = [savings[-1].copy()]
    current_currency_code = CurrencyExchanges.get_current_currency()
    current_currency_symbol = get_currency_symbol(current_currency_code)
    current_exchange = CurrencyExchanges.get_exchange_rate_by_currency_code(current_currency_code)
    savings_table[0][0] = current_currency_symbol + " - Assets"
    
    other_views = df_original[df_original['view_id'] != current_view]['view_id'].unique()
    for view in other_views:
        df = df_original[df_original['view_id']==view]
        next_view = create_balance_and_savings_table(df, current_view)[1][-1].copy()
        
        current_currency_code = CurrencyExchanges.get_currency_code_by_id(view)
        current_currency_symbol = get_currency_symbol(current_currency_code)
        next_view[0] = current_currency_symbol + " - Assets"
        active_exchange = CurrencyExchanges.get_exchange_rate_by_currency_code(current_currency_code)
        value_by_view = round(next_view[1] * current_exchange / active_exchange, 2)
        next_view[1] = value_by_view
        savings_table.append(next_view)
    savings_table = np.array(savings_table)
    savings_table = savings_table[savings_table[:, 1].argsort()[::-1]]
    total = round(sum(savings_table[:, 1]), 2)
    savings_table = np.concatenate((savings_table, np.array([['Total', float(total)]])), axis=0)
    
    savings_table[-1, -1] = float(savings_table[-1, -1])
    
    return result, savings, savings_table


def calculate_totals(df: pd.DataFrame):
    totals = df.groupby(['year', 'month', 'date']).agg(Amount=('Amount', 'sum')).reset_index()
    df = pd.concat([df, totals], ignore_index=True)
    df.fillna('Total', inplace=True)
    return df


def calculate_for_total_year_and_complete_totals(df: pd.DataFrame):
    sum_by_year = df.groupby(['category', 'year']).agg(Amount=('Amount', 'sum'), Amount_format=('Amount_format', 'sum')).reset_index()
    sum_by_year['month'] = 'Total Year'
    sum_by_year['date'] = pd.to_datetime(sum_by_year['year'].astype('str') + '-12-31')
    
    total_years = sum_by_year[sum_by_year['category']=='Total'].copy()
    sum_by_year = sum_by_year[sum_by_year['category']!='Total'].copy()
    sum_by_year = sum_by_year.sort_values(by=['year', 'Amount'], ascending=[True, False])
    sum_by_year = pd.concat([sum_by_year, total_years], ignore_index=True)
    
    total_sums = df.groupby(['category']).agg(Amount=('Amount', 'sum'), Amount_format=('Amount_format', 'sum')).reset_index()
    total_sums_total = total_sums[total_sums['category']=='Total'].copy()
    total_sums = total_sums[sum_by_year['category']!='Total'].copy()
    total_sums = total_sums.sort_values(by=['Amount'], ascending=[False])
    total_sums = pd.concat([total_sums, total_sums_total], ignore_index=True)
    
    total_sums['month'] = 'Total Year'
    total_sums['year'] = 'Total'
    total_sums['date'] = 'Total'
    
    df = pd.concat([df, sum_by_year, total_sums], ignore_index=True)
    
    return df


def create_dashboard_table_summaries_by_year_month(df: pd.DataFrame):
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['month_name'] = df['date'].dt.month_name()
    
    most_recent = max(df['date'])
    recent_month = most_recent.month
    recent_year = most_recent.year
    
    all_years = np.sort(df['year'].unique())
    all_months = np.sort(df['month'].unique())
    
    income_summary = df[df['type']=='Income'].groupby(['category', 'year', 'month']).agg(Amount=('amount', 'sum')).reset_index().sort_values(by=['year', 'month', 'Amount'], ascending=[False, False, False])
    income_summary['date'] = pd.to_datetime(dict(year=income_summary['year'], month=income_summary['month'], day=1))
    income_summary.rename(columns={'category': 'Income'}, inplace=True)
    income_summary = income_summary.reindex(columns=['Income', 'Amount', 'year', 'month', 'date'])
    income_summary = calculate_totals(income_summary)
    income_summary['Amount_format'] = income_summary['Amount'].copy()
    
    expenses_summary = df[df['type']=='Expenses'].groupby(['category', 'year', 'month']).agg(Amount=('amount', 'sum')).reset_index().sort_values(by='Amount', ascending=False)
    expenses_summary['date'] = pd.to_datetime(dict(year=expenses_summary['year'], month=expenses_summary['month'], day=1))
    expenses_summary.rename(columns={'category': 'Expenses'}, inplace=True)
    expenses_summary = expenses_summary.reindex(columns=['Expenses', 'Amount', 'year', 'month', 'date'])
    expenses_summary = calculate_totals(expenses_summary)
    expenses_summary['Amount_format'] = expenses_summary['Amount'].copy()
    
    savings = df[df['type']=='Income'].groupby(['Source/Target', 'year', 'month']).agg(Income=('amount', 'sum')).reset_index().sort_values(by='Income', ascending=False)
    savings.rename(columns={'Source/Target': 'Category'}, inplace=True)
    expenses_savings = df[df['type']=='Expenses'].groupby(['Source/Target', 'year', 'month']).agg(Expense=('amount', 'sum')).reset_index()
    expenses_savings.rename(columns={'Source/Target': 'Category'}, inplace=True)
    savings=pd.merge(left=savings, right=expenses_savings, on=['Category', 'year', 'month'], how='outer')
    
    savings_plus = df[df['type']=='Savings'].groupby(['category', 'year', 'month']).agg(Saveplus=('amount', 'sum')).reset_index()
    savings_plus.rename(columns={'category': 'Category'}, inplace=True)
    savings=pd.merge(left=savings, right=savings_plus, on=['Category', 'year', 'month'], how='outer')
    
    savings_minus = df[df['type']=='Savings'].groupby(['Source/Target', 'year', 'month']).agg(Saveminus=('amount', 'sum')).reset_index()
    savings_minus.rename(columns={'Source/Target': 'Category'}, inplace=True)
    savings=pd.merge(left=savings, right=savings_minus, on=['Category', 'year', 'month'], how='outer')
    
    savings.fillna(0, inplace=True)
    savings['Amount'] = savings['Income'] - savings['Expense'] + savings['Saveplus'] - savings['Saveminus']
    savings.drop(columns=['Income', 'Expense', 'Saveplus', 'Saveminus'], inplace=True)
    savings['date'] = pd.to_datetime(dict(year=savings['year'], month=savings['month'], day=1))
    savings.rename(columns={'Category': 'Savings'}, inplace=True)
    savings = savings.reindex(columns=['Savings', 'Amount', 'year', 'month', 'date'])
    savings = calculate_totals(savings)
    savings['Amount_format'] = savings['Amount'].copy()
    
    all_combs = np.array([str(year) + "-" + str(month) + "-01" for year in all_years for month in all_months])
    fillers = pd.DataFrame({'Savings': np.full(len(all_combs), "Total"), 'Amount_init': np.full(len(all_combs), 0), 'date': all_combs})
    fillers['date'] = pd.to_datetime(fillers['date'])
    fillers['year'] = fillers['date'].dt.year
    fillers['month'] = fillers['date'].dt.month
    
    savings_until = savings.copy()
    savings_until = pd.merge(left=savings_until, right=fillers, how='outer', on=['Savings', 'date', 'year', 'month'])
    savings_until.drop(columns=['Amount_format', 'Amount_init'], inplace=True)
    savings_until = savings_until.pivot(index='date', columns='Savings', values='Amount')
    savings_until.fillna(0, inplace=True)
    
    savings_until = savings_until.unstack().reset_index().rename(columns={0: 'Amount'})
    savings_until['year'] = savings_until['date'].dt.year
    savings_until['month'] = savings_until['date'].dt.month
    savings_until['cumsum'] = savings_until.groupby('Savings')['Amount'].transform(pd.Series.cumsum)
    savings_until.drop(columns=['Amount'], inplace=True)
    savings_until.rename(columns={'cumsum': 'Amount'}, inplace=True)
    savings_until = savings_until.reindex(columns=['Savings', 'Amount', 'year', 'month', 'date']).sort_values(by=['date', 'Amount'], ascending=[True, False])
    savings_totals = savings_until[savings_until['Savings']=='Total'].copy()
    savings_until.drop(savings_until[savings_until['Savings']=='Total'].index, inplace=True)
    savings_until = pd.concat([savings_until, savings_totals], ignore_index=True)
    savings_until['Amount'] = savings_until['Amount'].apply(lambda x: round(x, 2))
    savings_until['Amount_format'] = savings_until['Amount'].copy()
    
    
    income_summary.rename(columns={'Income': 'category'}, inplace=True)
    expenses_summary.rename(columns={'Expenses': 'category'}, inplace=True)
    savings.rename(columns={'Savings': 'category'}, inplace=True)
    savings_until.rename(columns={'Savings': 'category'}, inplace=True)
    
    income_summary = calculate_for_total_year_and_complete_totals(income_summary)
    expenses_summary = calculate_for_total_year_and_complete_totals(expenses_summary)
    savings = calculate_for_total_year_and_complete_totals(savings)
    savings_until = calculate_for_total_year_and_complete_totals(savings_until)
    
    all_months = np.concat((all_months, ['Total']))
    all_years = np.concat((all_years, ['Total']))
    
    return [all_years, all_months, income_summary, expenses_summary, savings, savings_until, recent_month, recent_year]


def initiate_dashboard_tables_and_summaries(df: pd.DataFrame, current_view: int):
    all_years, all_months, incomes, expenses, savings, savings_until, recent_month, recent_year = create_dashboard_table_summaries_by_year_month(df[df['view_id']==current_view].copy())
    
    # Get totals from savings_until_table of current view
    totals = savings_until
    totals = totals[totals['category']=='Total'].copy()
    current_currency_code = CurrencyExchanges.get_current_currency()
    current_currency_symbol = get_currency_symbol(current_currency_code)
    totals['category'] = current_currency_symbol + " - Assets"
    all_totals = [totals]
    
    # Now get totals from savings_until from the other views.
    current_exchange = CurrencyExchanges.get_exchange_rate_by_currency_code(current_currency_code)
    other_views = df[df['view_id']!=current_view]['view_id'].unique()
    for view in other_views:
        other_results = create_dashboard_table_summaries_by_year_month(df[df['view_id']==view].copy())[5]
        other_totals = other_results[other_results['category']=='Total'].copy()
        current_currency_code = CurrencyExchanges.get_currency_code_by_id(view)
        current_currency_symbol = get_currency_symbol(current_currency_code)
        other_totals['category'] = current_currency_symbol + " - Assets"
        active_exchange = CurrencyExchanges.get_exchange_rate_by_currency_code(current_currency_code)
        other_totals['Amount'] = round(other_totals['Amount'] * current_exchange / active_exchange, 2)
        all_totals.append(other_totals)
    
    # Concatenate all savings into 1 dataframe
    total_savings = pd.concat(all_totals, ignore_index=True).sort_values(by='Amount', ascending=False)
    total_savings = calculate_totals(total_savings)
    
    # print(recent_month)
    
    return all_years, all_months, incomes, expenses, savings, savings_until, recent_month, recent_year, total_savings