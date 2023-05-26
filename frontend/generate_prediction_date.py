import streamlit as st
import datetime

def generate_prediction_date():
    suggested_dates= datetime.date(2022, 8, 1)
    prediction_date = st.date_input("Choose a Date to Predict:",
                                         suggested_dates,
                                         key="test",
                                         )
    return prediction_date
