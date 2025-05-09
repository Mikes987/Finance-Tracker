# import plotly.graph_objects as go
import json
import plotly
import plotly.express as px
import pandas as pd

def create_date_chart(df: pd.DataFrame):
    # fig = go.Figure([go.Scatter(x=df['date'], y=df['Balance'])])
    df['Balance'] = df['Balance'].astype(int)
    fig = px.line(df, x='date', y='Balance')
    return fig.to_html(full_html=False)