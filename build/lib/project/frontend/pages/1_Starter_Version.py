import streamlit as st
import datetime
import requests
import pandas as pd
import sys
import matplotlib.pyplot as plt
import os

root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

sys.path.append(root_path)

from project.frontend.py_logic.baseline_model import baseline_model
from project.frontend.py_logic.visualize import plotting, nice_plotting

f"{root_path}"

#Sidebar
with st.sidebar:
    '''
    ### Back to the future
    Check out the model's performance "back in the day"
    '''
    demo_date= datetime.date(2022, 8, 1)

    prediction_date = st.date_input("Prediction Date", demo_date, key=None, help=None)


#Main Panel
'''
# Fortune Frontier
'''

'''
#### Forecasted Revenues:
'''

df = baseline_model()
df = df.rename(columns={'ds': 'Day', 'yhat_lower': 'Low Prediction', 'yhat': 'Mid Prediction', 'yhat_upper': 'High Prediction', 'y_true': 'True Value', 'error': 'Error (MAE)'})
df['Day'] = df['Day'].dt.date

# CSS to inject contained in a stringS
hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """
# Inject CSS with Markdown
st.markdown(hide_table_row_index, unsafe_allow_html=True)

# Display a static table
st.table(df)


'''
&nbsp;
&nbsp;
#### Forecast's Performance:
'''
plot = plotting()
st.pyplot(plot)

nice_plot = nice_plotting()
st.pyplot(nice_plot)
