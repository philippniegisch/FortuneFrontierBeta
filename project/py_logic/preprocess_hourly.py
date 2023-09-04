import pandas as pd
import numpy as np
import pandas as pd
import os
import io
import streamlit as st
import datetime

@st.cache_data
def preprocess_complete():
    #df data
    #import raw revenue data
    df_2016 = pd.read_csv("raw_data/orders2016.csv", sep=";")
    df_2017 = pd.read_csv("raw_data/orders2017.csv", sep=";")
    df_2018 = pd.read_csv("raw_data/orders2018.csv", sep=";")
    df_2019 = pd.read_csv("raw_data/orders2019.csv", sep=";")
    df_2020 = pd.read_csv("raw_data/orders2020.csv", sep=";")
    df_2021 = pd.read_csv("raw_data/orders2021.csv", sep=";")
    df_2022 = pd.read_csv("raw_data/orders2022.csv", sep=";")

    df_list = [df_2016, df_2017, df_2018, df_2019, df_2020, df_2021, df_2022]

    #create hourly revenue data
    for df in df_list:
        df['time'] = df['time'].astype(str)

    for i, df in enumerate(df_list):
        # Convert 'date' column to datetime dtype
        df['date'] = pd.to_datetime(df['date'])

        # Extract the hour from 'time' column
        df['hour'] = df['time'].apply(lambda x: int(x.split(':')[0]))

        # Create combined datetime object using date and hour
        df['date_hour'] = df.apply(lambda row: datetime.datetime(row['date'].year, row['date'].month, row['date'].day, row['hour']), axis=1)

        df_list[i] = pd.DataFrame(df.groupby(by="date_hour")["item_price"].sum()/100)

    #Concat all data in one dataframe, rename the columns for prophet
    df = pd.concat(df_list, ignore_index=False)
    df = df.rename(columns={"date_hour": "ds", "item_price": "y"})
    df["ds"] = df.index
    df = df.reset_index(drop=True)
    df = df[["ds","y"]]

    #turning the ds (date) column into datetime
    df['ds']=pd.to_datetime(df['ds'])

    #LOADING HISTORIC WEATHER DATA
    weather_df = pd.read_csv('feature_data/weather.csv')

    weather_df = weather_df.drop(columns=['dt', 'timezone', 'city_name', 'lat', 'lon',
        'visibility', 'dew_point', 'feels_like', 'temp_min', 'temp_max',
        'pressure', 'sea_level', 'grnd_level', 'wind_gust', 'rain_3h', 'snow_1h', 'snow_3h', 'weather_id', 'weather_main', 'weather_description',
        'weather_icon','wind_deg'])

    weather_df = weather_df.fillna(0)
    weather_df['dt_iso'] = weather_df['dt_iso'].str[:19]
    weather_df = weather_df.rename(columns={'dt_iso': 'ds'})
    weather_df['ds']=pd.to_datetime(weather_df['ds'])

    #MERGING features with df
    merged_df = pd.merge(df,weather_df,how="left")

    #Correcting GCP capitalization of dtypes - int
    for col in merged_df.columns:
        if pd.api.types.is_integer_dtype(merged_df[col]):
            merged_df[col] = merged_df[col].astype('int64')

    #Correcting GCP capitalization of dtypes - float
    merged_df["y"]=merged_df["y"].astype("float64")

    return merged_df
