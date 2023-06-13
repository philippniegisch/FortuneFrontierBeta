import streamlit as st
from config import PAGE_CONFIG_SET
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
from project.py_logic.visualize_b import nice_plotting
from project.py_logic.regressor_model_b import regressor_model

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
columnl.markdown("### *BETA - Back to the future edition*")
suggested_dates= datetime.date(2022, 8, 1)
prediction_date = columnl.date_input("Choose a Date to Predict:", suggested_dates, key="original", help=None)

#right header column
columnr.markdown(" ")
columnr.markdown(" ")
columnr.markdown(" ")
columnr.image(image, caption= "First Use Case: Woop Woop Ice Cream Berlin", width = 400)


#prediction
st.markdown("### Your Predicted Fortune: :crystal_ball:")
st.markdown("---")

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
                                'error': 'Error',
                                'mae%': 'Error %'})
        #df['Day'] = df['Day'].dt.date
        df_mini = table_df[["Day", "Prediction", "Error %"]].iloc[1:]
        styled_df = table_df.style.format({'Low Prediction': "{:.2f}",
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

        nice_plot = nice_plotting(df)
        nice_plot.update_layout(width=800, height=400)

        #Main metrics
        m1, m2, m3, m4, m5 = st.columns((1,1,1,1,1))

        m1.write('')
        m2.metric(label ="Today's Prediction",value = str(int(table_df["Prediction"].iloc[0]))+"€")
        m3.metric(label ="Today's Error %" ,value = str(int(table_df['Error %'].iloc[0]))+"%")
        m4.metric(label = 'Historic True Value',value = str(int(table_df['True Value'].iloc[0]))+"€")
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
        st.markdown("# Sorry Fortune Frontier Fandom :heart:, but the store was closed on day selected, try again! :sparkles:")
        st.markdown("### Hint :jigsaw:: try months outside of winter and before the store closed in November 2022")
