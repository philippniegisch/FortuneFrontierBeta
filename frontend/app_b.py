import streamlit as st
from config import PAGE_CONFIG_SET
import datetime
import requests
import pandas as pd
import sys
import matplotlib.pyplot as plt
import os
from PIL import Image
import plotly.express as px


#access project package
root_path = os.path.dirname(os.path.dirname(__file__))
sys.path.append(root_path)
from project.py_logic.baseline_model import baseline_model
from project.py_logic.visualize_b import nice_plotting
from project.py_logic.regressor_model_b import regressor_model
from project.py_logic.regressor_model_hourly import regressor_model_hourly
from project.py_logic.preprocess_b import preprocess_revenue

#streamlit page configuration check
if not PAGE_CONFIG_SET:
    # Set the page configuration
    st.set_page_config(
    page_title="Fortune Frontier Beta",
    page_icon=":coin:",
    layout="wide"
    )

#remove chart warning
st.set_option('deprecation.showPyplotGlobalUse', False)

#image setup
image_path = os.path.join(root_path, 'frontend', 'images', 'woopwoop.png')
image = Image.open(image_path)

columnl, columnm, columnr = st.columns([19,11,12])

#left header column
columnl.markdown("# :coin: Fortune Frontier :coin:")
columnl.markdown("##### *BETA - Back to the future edition*")
suggested_dates= datetime.date(2022, 8, 1)
prediction_date = columnl.date_input("Choose a Date to Predict:", suggested_dates, key="original", help=None)
columnl.markdown("### Your Daily Hourly and 16-Day Revenue Forecast: :crystal_ball:")
#columnl.markdown("###### *Leveraging Machine Learning and Historical Data to predict your Future Fortune*")

#right header column
columnr.markdown(" ")
columnr.markdown(" ")
columnr.markdown(" ")
columnr.image(image, caption= "First Use Case: Woop Woop Ice Cream Berlin", width = 400)


#prediction
#st.markdown("### Your 16-day Revenue Forecast: :crystal_ball:")
st.markdown("###### *Leveraging Machine Learning and Historical Data to predict your Future Fortune*")

tab1, tab2, tab3, tab4= st.tabs(["Hourly", "16-Day", "Revenue Wheel", "Easter Egg"])

with tab1:
    st.header("Hourly Forecast")
    st.write(prediction_date)
    with st.spinner('⏰⬅️🚗💨⚡️ Updating Report...'):
        #df cleaning
        df = regressor_model_hourly(prediction_date)

        #check if string or df
        if isinstance(df, pd.DataFrame) == True:

            #if dataframe
            table_df = df.rename(columns={'ds': 'Day',
                                    'yhat_lower': 'Low Prediction',
                                    'yhat': 'Prediction',
                                    'yhat_upper': 'High Prediction',
                                    'y_true': 'True Value',
                                    'error': 'Prediction Error',
                                    'me%': 'Prediction Error %'})
            #df['Day'] = df['Day'].dt.date
            df_mini = table_df[["Day", "Prediction", "True Value", "Prediction Error %"]].iloc[1:]
            styled_df = table_df.style.format({'Low Prediction': "{:.2f}",
                                            'Prediction': "{:.2f}",
                                            'High Prediction': "{:.2f}",
                                            'True Value': "{:.2f}",
                                            'Prediction Error': "{:.2f}",
                                            'Prediction Error %': "{:.2f}"})
            stlyed_df_mini = df_mini.style.format({ 'Prediction': "{:.2f}",
                                                   'True Value': "{:.2f}",
                                                   'Prediction Error %': "{:.2f}"})

            # CSS to inject contained in a stringS
            hide_table_row_index = """
                        <style>
                        thead tr th:first-child {display:none}
                        tbody th {display:none}
                        </style>
                        """
            # Inject CSS with Markdown
            st.markdown(hide_table_row_index, unsafe_allow_html=True)

            nice_plot = nice_plotting(df)
            nice_plot.update_layout(width=800, height=400)

            #Main metrics
            m1, m2, m3, m4, m5 = st.columns((1,1,1,1,1))

            m1.write('')
            m2.metric(label ="Today's Revenue Prediction",value = str(int(table_df["Prediction"].sum()))+"€")
            m3.metric(label ="Today's Revenue Prediction Error %" ,value = str(int((table_df['Prediction'].sum()-table_df['True Value'].sum())/table_df['True Value'].sum()*100))+"%")
            m4.metric(label = 'Historic True Revenue',value = str(int(table_df['True Value'].sum()))+"€")
            m5.write('')

            #Main table and chart
            column1, column2 = st.columns([2, 3])

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
            st.markdown("# Sorry Fortune Frontier Fandom :heart:, but the store was closed on day selected, try again! :sparkles:")
            st.markdown("### Hint :jigsaw:: try months outside of winter and before the store closed in November 2022")

with tab2:
    st.header("16-Day Forecast")
    st.write(prediction_date)
    with st.spinner('⏰⬅️🚗💨⚡️ Updating Report...'):
        #df cleaning
        df = regressor_model(prediction_date)

        #check if string or df
        if isinstance(df, pd.DataFrame) == True:

            #if dataframe
            table_df = df.rename(columns={'ds': 'Day',
                                    'yhat_lower': 'Low Prediction',
                                    'yhat': 'Prediction',
                                    'yhat_upper': 'High Prediction',
                                    'y_true': 'True Value',
                                    'error': 'Prediction Error',
                                    'me%': 'Prediction Error %'})
            table_df["Day"] = table_df["Day"].dt.date
            #df['Day'] = df['Day'].dt.date
            df_mini = table_df[["Day", "Prediction", "True Value", "Prediction Error %"]].iloc[1:]
            styled_df = table_df.style.format({'Low Prediction': "{:.2f}",
                                            'Prediction': "{:.2f}",
                                            'High Prediction': "{:.2f}",
                                            'True Value': "{:.2f}",
                                            'Prediction Error': "{:.2f}",
                                            'Prediction Error %': "{:.2f}"})
            stlyed_df_mini = df_mini.style.format({ 'Prediction': "{:.2f}",
                                            'True Value': "{:.2f}",
                                            'Prediction Error %': "{:.2f}"})

            # CSS to inject contained in a stringS
            hide_table_row_index = """
                        <style>
                        thead tr th:first-child {display:none}
                        tbody th {display:none}
                        </style>
                        """
            # Inject CSS with Markdown
            st.markdown(hide_table_row_index, unsafe_allow_html=True)

            nice_plot = nice_plotting(df)
            nice_plot.update_layout(width=800, height=400)

            #Main metrics
            m1, m2, m3, m4, m5 = st.columns((1,1,1,1,1))

            m1.write('')
            m2.metric(label ="Today's Revenue Prediction",value = str(int(table_df["Prediction"].iloc[0]))+"€")
            m3.metric(label ="Today's Revenue Prediction Error %" ,value = str(int(table_df['Prediction Error %'].iloc[0]))+"%")
            m4.metric(label = 'Historic True Revenue',value = str(int(table_df['True Value'].iloc[0]))+"€")
            m5.write('')

            #Main table and chart
            column1, column2 = st.columns([2, 3])

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
            st.markdown("# Sorry Fortune Frontier Fandom :heart:, but the store was closed on day selected, try again! :sparkles:")
            st.markdown("### Hint :jigsaw:: try months outside of winter and before the store closed in November 2022")

with tab3:
    st.header("Wheel of Fortune")
    st.write(prediction_date)
    with st.spinner('⏰⬅️🚗💨⚡️ Updating Report...'):

        #Dataset is loaded as df
        df = preprocess_revenue()

        df.rename(columns={'y': 'Revenue'}, inplace=True)

        # Expanding dates for complete dates
        min_date = pd.to_datetime("2016-01-01")
        max_date = pd.to_datetime("2022-12-31")
        all_dates = pd.date_range(min_date, max_date, freq='D')
        df = df.set_index('ds').reindex(all_dates).reset_index().rename(columns={'index': 'ds'})

        # Reset index to start from 0
        df = df.reset_index(drop=True)

        #Fill missing values with zeros
        df['Revenue'] = df['Revenue'].fillna(0)

        #Creating seasonal columns
        df['Year'] = df['ds'].dt.year
        df['Season'] = df['ds'].dt.quarter.map({1: 'Winter', 2: 'Spring', 3: 'Summer', 4: 'Fall'})
        df['Month'] = df['ds'].dt.month_name()
        df['Week'] = df['ds'].dt.isocalendar().week
        df['Weekday'] = df['ds'].dt.strftime('%A')

        # Compute total revenue and fill missing values with zeros
        total_revenue = df['Revenue'].sum()

        # Prepare the data
        df_hierarchy = df.groupby(['Year', 'Season', 'Month', 'Week', 'Weekday'], as_index=False)['Revenue'].sum()

        # Filter out rows with zero revenue
        df_hierarchy = df_hierarchy[df_hierarchy['Revenue'] != 0]

        # Create the Sunburst chart
        fig = px.sunburst(df_hierarchy, path=['Year', 'Season', 'Month', 'Week', 'Weekday'], values='Revenue', color='Revenue')
        fig.update_traces(sort=False, customdata=df_hierarchy[['Year','Season', 'Month', 'Week']], selector=dict(type='sunburst'))
        st.plotly_chart(fig)

with tab4:
    st.header("An owl, you're welcome")
    st.image("https://static.streamlit.io/examples/owl.jpg", width=200)
