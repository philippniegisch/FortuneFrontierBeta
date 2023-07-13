import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import plot
from plotly.io import to_html
from dash import Dash, dcc, html
import streamlit as st
import streamlit.components.v1 as components
import sys
import os

#access project package
root_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(root_path)
# DELETE st.markdown(f"{root_path}")
from project.py_logic.preprocess_b import preprocess_revenue

# Load dataframe here!!!
df = preprocess_revenue()

# Group by year and calculate the sum of 'y'
df_yearly = df.groupby(df['ds'].dt.year)['y'].sum().reset_index()

# Rename the columns in the resulting dataframe
df_yearly.columns = ['year', 'sum_y']

# Create a Streamlit app
st.title("Streamlit Dash Integration")

# Create a Dash app
dash_app = Dash(__name__)

def bar_chart():

    fig = go.Figure([go.Bar(x=df_yearly['year'], y=df_yearly['sum_y'], marker_color='indianred')])
    fig.update_layout(title='Revenue per Year',
                 xaxis_title = 'Year',
                 yaxis_title = 'Revenue in €')
    return fig

def scatter_plot():

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['ds'],y=df['y'], mode='markers'))
    return fig

dash_app.layout = html.Div(
    id='parent',
    children=[
        html.H1(
            id='h1',
            children='Data Analytics Dashboard',
            style={'textAlign': 'center', 'marginTop': 25, 'marginBottom': 25}
        ),
        html.Div(
            id='bar_div',
            children=[dcc.Graph(id='bar_plot', figure=bar_chart())],
            style={'width': '50%', 'display': 'inline-block'}
        ),
        html.Div(
            id='scatter_div',
            children=[dcc.Graph(id='scatter_plot', figure=scatter_plot())],
            style={'width': '50%', 'display': 'inline-block'}
        ),
    ]
)

# Convert the Dash app to HTML
dash_app_html = dash_app.to_html()

# Render the Dash app within Streamlit
components.html(dash_app_html, height=500)
