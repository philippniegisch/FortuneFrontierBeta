import streamlit as st
import datetime
import requests
import pandas as pd
import sys
import matplotlib.pyplot as plt
import os
from PIL import Image

#access project package
root_path = os.path.dirname(os.path.dirname(__file__))
sys.path.append(root_path)
from project.py_logic.baseline_model import baseline_model
from project.py_logic.visualize import nice_plotting

#streamlit page configuration
st.set_page_config(
    page_title="Fortune Frontier",
    page_icon=":coin:",
    layout="wide"
)

#remove chart warning
st.set_option('deprecation.showPyplotGlobalUse', False)

#image setup
image_path = os.path.join(root_path, 'frontend', 'images', 'woopwoop.png')
image = Image.open(image_path)

#csv downloads
df06_path = os.path.join(root_path, 'output_data/prediction_06.csv')
df06 = pd.read_csv(df06_path)
df08_path = os.path.join(root_path, 'output_data/prediction_08.csv')
df08 = pd.read_csv(df08_path)
df10_path = os.path.join(root_path, 'output_data/prediction_10.csv')
df10 = pd.read_csv(df10_path)

columnl, columnm, columnr = st.columns([19,11,12])

#left header column
columnl.markdown("# :coin: Fortune Frontier :coin:")
columnl.markdown("### *BETA - Back to the future edition*")
#columnl.markdown("Check out the model's performance 'back in the day'")
suggested_dates= datetime.date(2022, 8, 1)
#, datetime.date(2022, 6, 03), datetime.date(2022, 10, 14)]
prediction_date = columnl.date_input("Choose a Date to Predict:", suggested_dates, key=None, help=None)


#right header column
columnr.markdown(" ")
columnr.markdown(" ")
columnr.markdown(" ")
columnr.image(image, caption= "First Use Case: Woop Woop Ice Cream Berlin", width = 400)



st.markdown("### Your Predicted Fortune: :crystal_ball:")
st.markdown("---")
if prediction_date == datetime.date(2022, 8, 1):
    st.write(prediction_date)
    with st.spinner('⏰⬅️🚗💨⚡️ Updating Report...'):
        #df cleaning
        df = df08.iloc[:,1:]
        df = df.rename(columns={'ds': 'Day',
                                'yhat_lower': 'Low Prediction',
                                'yhat': 'Prediction',
                                'yhat_upper': 'High Prediction',
                                'y_true': 'True Value',
                                'error': 'Error',
                                'mae%': 'Error %'})
        #df['Day'] = df['Day'].dt.date
        df_mini = df[["Day", "Prediction", "Error %"]].iloc[1:]
        styled_df = df.style.format({'Low Prediction': "{:.2f}",
                                     'Prediction': "{:.2f}",
                                     'High Prediction': "{:.2f}",
                                     'True Value': "{:.2f}",
                                     'Error': "{:.2f}",
                                     'Error %': "{:.2f}"})
        stlyed_df_mini = df_mini.style.format({ 'Prediction': "{:.2f}",
                                     'Error %': "{:.2f}"})

        # CSS to inject contained in a stringS
        hide_table_row_index = """
                    <style>
                    thead tr th:first-child {display:none}
                    tbody th {display:none}
                    </style>
                    """
        # Inject CSS with Markdown
        st.markdown(hide_table_row_index, unsafe_allow_html=True)

        nice_plot = nice_plotting(df08)
        nice_plot.update_layout(width=800, height=400)

        #Main metrics
        m1, m2, m3, m4, m5 = st.columns((1,1,1,1,1))

        m1.write('')
        m2.metric(label ="Today's Prediction",value = str(int(df["Prediction"].iloc[0]))+"€")
        m3.metric(label ="Today's Error %" ,value = str(int(df['Error %'].iloc[0]))+"%")
        m4.metric(label = 'Historic True Value',value = str(int(df['True Value'].iloc[0]))+"€")
        m5.write('')

        #Main table and chart
        column1, column2 = st.columns([1, 2])

        #Main table
        column1.markdown("#### Forecasted Revenues:")
        column1.table(stlyed_df_mini)

        column2.markdown("#### Forecast Performance:")
        column2.plotly_chart(nice_plot,use_container_width=True, use_container_height=True)

        #Full table
        '''
        #### Full Forecast View:
        '''
        st.table(styled_df)

elif prediction_date == datetime.date(2022, 10, 14):
    st.write(prediction_date)
    with st.spinner('⏰⬅️🚗💨⚡️ Updating Report...'):
        #df cleaning
        df = df10.iloc[:,1:]
        df = df.rename(columns={'ds': 'Day',
                                'yhat_lower': 'Low Prediction',
                                'yhat': 'Prediction',
                                'yhat_upper': 'High Prediction',
                                'y_true': 'True Value',
                                'error': 'Error',
                                'mae%': 'Error %'})
        #df['Day'] = df['Day'].dt.date
        df_mini = df[["Day", "Prediction", "Error %"]].iloc[1:]
        styled_df = df.style.format({'Low Prediction': "{:.2f}",
                                     'Prediction': "{:.2f}",
                                     'High Prediction': "{:.2f}",
                                     'True Value': "{:.2f}",
                                     'Error': "{:.2f}",
                                     'Error %': "{:.2f}"})
        stlyed_df_mini = df_mini.style.format({ 'Prediction': "{:.2f}",
                                     'Error %': "{:.2f}"})

        # CSS to inject contained in a stringS
        hide_table_row_index = """
                    <style>
                    thead tr th:first-child {display:none}
                    tbody th {display:none}
                    </style>
                    """
        # Inject CSS with Markdown
        st.markdown(hide_table_row_index, unsafe_allow_html=True)

        nice_plot = nice_plotting(df10)
        nice_plot.update_layout(width=800, height=400)

        #Main metrics
        m1, m2, m3, m4, m5 = st.columns((1,1,1,1,1))

        m1.write('')
        m2.metric(label ="Today's Prediction",value = str(int(df["Prediction"].iloc[0]))+"€")
        m3.metric(label ="Today's Error %" ,value = str(int(df['Error %'].iloc[0]))+"%")
        m4.metric(label = 'Historic True Value',value = str(int(df['True Value'].iloc[0]))+"€")
        m5.write('')

        #Main table and chart
        column1, column2 = st.columns([1, 2])

        #Main table
        column1.markdown("#### Forecasted Revenues:")
        column1.table(stlyed_df_mini)

        column2.markdown("#### Forecast Performance:")
        column2.plotly_chart(nice_plot,use_container_width=True, use_container_height=True)

        #Full table
        '''
        #### Full Forecast View:
        '''
        st.table(styled_df)
else:
    st.write(prediction_date)
    with st.spinner('⏰⬅️🚗💨⚡️ Updating Report...'):
        #df cleaning
        df = df06.iloc[:,1:]
        df = df.rename(columns={'ds': 'Day',
                                'yhat_lower': 'Low Prediction',
                                'yhat': 'Prediction',
                                'yhat_upper': 'High Prediction',
                                'y_true': 'True Value',
                                'error': 'Error',
                                'mae%': 'Error %'})
        #df['Day'] = df['Day'].dt.date
        df_mini = df[["Day", "Prediction", "Error %"]].iloc[1:]
        styled_df = df.style.format({'Low Prediction': "{:.2f}",
                                     'Prediction': "{:.2f}",
                                     'High Prediction': "{:.2f}",
                                     'True Value': "{:.2f}",
                                     'Error': "{:.2f}",
                                     'Error %': "{:.2f}"})
        stlyed_df_mini = df_mini.style.format({ 'Prediction': "{:.2f}",
                                     'Error %': "{:.2f}"})

        # CSS to inject contained in a stringS
        hide_table_row_index = """
                    <style>
                    thead tr th:first-child {display:none}
                    tbody th {display:none}
                    </style>
                    """
        # Inject CSS with Markdown
        st.markdown(hide_table_row_index, unsafe_allow_html=True)

        nice_plot = nice_plotting(df06)
        nice_plot.update_layout(width=800, height=400)

        #Main metrics
        m1, m2, m3, m4, m5 = st.columns((1,1,1,1,1))

        m1.write('')
        m2.metric(label ="Today's Prediction",value = str(int(df["Prediction"].iloc[0]))+"€")
        m3.metric(label ="Today's Error %" ,value = str(int(df['Error %'].iloc[0]))+"%")
        m4.metric(label = 'Historic True Value',value = str(int(df['True Value'].iloc[0]))+"€")
        m5.write('')

        #Main table and chart
        column1, column2 = st.columns([1, 2])

        #Main table
        column1.markdown("#### Forecasted Revenues:")
        column1.table(stlyed_df_mini)

        column2.markdown("#### Forecast Performance:")
        column2.plotly_chart(nice_plot,use_container_width=True, use_container_height=True)

        #Full table
        '''
        #### Full Forecast View:
        '''
        st.table(styled_df)
