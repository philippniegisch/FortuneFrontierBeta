import streamlit as st
import datetime
import requests
import pandas as pd
import sys

sys.path.append('/home/tearkistan/code/philippniegisch/fortunefrontier/project')
from py_logic.baseline_model import baseline_model

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
df
'''
&nbsp;
&nbsp;
#### Forecast's Performance:
-insert plot with historic + predicted + rmse vs actual here>-
'''
