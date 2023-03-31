import streamlit as st
import datetime
import requests
import pandas as pd
from PIL import Image
import os



st.set_page_config(
    page_title="Fortune Frontier",
    page_icon=":money_with_wings:",
)

'''
# :money_with_wings: Fortune Frontier :money_with_wings:
## Your 7-Day Revenue Forecast
&nbsp;
&nbsp;
&nbsp;
### Our mission is to help food business owners optimize their operations with the power of Data Science!
&nbsp;
&nbsp;
### A Woop Woop Ice Cream Berlin Story:
'''

#print(os.path.dirname(os.path.dirname(__file__)))

root_path = os.path.dirname(os.path.dirname(__file__))
image_path = os.path.join(root_path, 'frontend', 'images', 'woopwoop.png')

image = Image.open(image_path)

st.image(image, caption= "Our Use Case: Woop Woop Ice Cream", width = 500)


#st.markdown(f"<h3 style='text-align: center;'>Our mission is to help food business owners optimize their operations with the power of Data Science!</h3>", unsafe_allow_html=True)
