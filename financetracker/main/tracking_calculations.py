import pandas as pd
import numpy as np
from datetime import date

def create_balance_and_savings_table(df: pd.DataFrame):
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
    df_sums = df.groupby(df['date']).agg(Curr=('curr', 'sum')).reset_index().sort_values(by=['date'])
    df_sums['Balance'] = df_sums['Curr'].cumsum()
    df_sums.drop(columns=['Curr'], inplace=True)
    
    df = df.merge(df_sums).sort_values(by='date', ascending=False)
    del df_sums
    df.drop(columns=['sign', 'curr'], inplace=True)
    df = df.reindex(columns=['date', 'type', 'category', 'amount', 'Source/Target', 'comment', 'Balance', 'id'])
    
    df['date'] = pd.to_datetime(df['date'])
    df['id'] = df['id'].astype('int64')
    
    return df, df_savings.values


def calculate_totals(df: pd.DataFrame):
    totals = df.groupby(['year', 'month', 'date']).agg(Amount=('Amount', 'sum')).reset_index()
    df = pd.concat([df, totals], ignore_index=True)
    df.fillna('Total', inplace=True)
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
    
    expenses_summary = df[df['type']=='Expenses'].groupby(['category', 'year', 'month']).agg(Amount=('amount', 'sum')).reset_index().sort_values(by='Amount', ascending=False)
    expenses_summary['date'] = pd.to_datetime(dict(year=expenses_summary['year'], month=expenses_summary['month'], day=1))
    expenses_summary.rename(columns={'category': 'Expenses'}, inplace=True)
    expenses_summary = expenses_summary.reindex(columns=['Expenses', 'Amount', 'year', 'month', 'date'])
    expenses_summary = calculate_totals(expenses_summary)
    
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
    
    savings_until = savings.copy()
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
    
    return all_years, all_months, income_summary, expenses_summary, savings, savings_until, recent_month, recent_year