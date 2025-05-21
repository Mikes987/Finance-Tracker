# import plotly.graph_objects as go
import json
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def create_date_chart(df: pd.DataFrame, currency_symbol):
    # df['Balance'] = df['Balance'].astype(int)
    fig = go.Figure(go.Scatter(x=df['date'],
                               y=df['Balance'],
                               hovertemplate='%{x}: <extra> %{y} </extra>'))
    # fig = px.line(df, x='date', y='Balance', template="plotly_white")
    
    fig.update_layout(template='plotly_white',
                      title=dict(text="Balance over Time"),
                      xaxis=dict(title=dict(text='Date')),
                      yaxis=dict(title=dict(text='Balance in ' + currency_symbol)))
    fig.update_yaxes(ticksuffix=' ' + currency_symbol, tickformat=',')
    return fig.to_html(full_html=False)