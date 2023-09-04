
from prophet import Prophet
from .preprocess_hourly import preprocess_complete
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime as dt
from datetime import timedelta


def regressor_model_hourly(prediction_date):

    #Load feature dataframe
    feature_df = preprocess_complete()

    #LOADING AND PREPROCESSING WEATHER PREDICTIONS
    weather_forecast_df = pd.read_csv("raw_data/weather_forecast_2018_2023.csv")
    weather_forecast_df = weather_forecast_df.drop(columns=["forecast dt unixtime","convective","wind_deg","accumulated","hours","rate","slice dt unixtime","lat","lon","dew_point","snow_depth","snow","pressure","ground_pressure","ice","fr_rain"])

    # Convert to datetime using the format with only %z for timezone and remove the extra +0000
    weather_forecast_df['forecast dt iso'] = pd.to_datetime(weather_forecast_df['forecast dt iso'].str.replace(' UTC', ''), format='ISO8601')
    weather_forecast_df['slice dt iso'] = pd.to_datetime(weather_forecast_df['slice dt iso'].str.replace(' UTC', ''), format='ISO8601')

    # rain_probability
    weather_forecast_df['rain_probability'] = weather_forecast_df['rain'] * weather_forecast_df['probability']
    print(weather_forecast_df.head())
    '''
    # Remove the ' UTC' part from the datetime strings
    weather_forecast_df['forecast dt iso'] = weather_forecast_df['forecast dt iso'].str.replace(' UTC', '')
    weather_forecast_df['slice dt iso'] = weather_forecast_df['slice dt iso'].str.replace(' UTC', '')

    # Convert to datetime using the format with only %z for timezone
    weather_forecast_df['forecast dt iso'] = pd.to_datetime(weather_forecast_df['forecast dt iso'], format='%Y-%m-%d %H:%M:%S')
    weather_forecast_df['slice dt iso'] = pd.to_datetime(weather_forecast_df['slice dt iso'], format='%Y-%m-%d %H:%M:%S')

    # rain_probability
    weather_forecast_df['rain_probability'] = weather_forecast_df['rain'] * weather_forecast_df['probability']
    '''

    #set the index
    weather_forecast_df.reset_index(drop=True, inplace=True)

    weather_forecast_df = weather_forecast_df.drop(columns=['rain','probability'])
    weather_forecast_df = weather_forecast_df.rename(columns={'temperature':'temp','rain_probability': 'rain_1h', 'slice dt iso':'ds', 'clouds':'clouds_all'})

    #Setting variables
    horizon = 13
    opening_hour = 12
    closing_hour = 23

    #CLEANING DATA
    cleaned_df = feature_df[(feature_df['ds'].dt.hour >= opening_hour) & (feature_df['ds'].dt.hour <= closing_hour)]
    cleaned_df = cleaned_df[cleaned_df["y"]<=500]
    cleaned_df =  cleaned_df.reset_index(drop=True)

    #SPLITTING DATA
    split_date = str(prediction_date) + " 13:00:00"
    datetime_split = dt.strptime(split_date, "%Y-%m-%d %H:%M:%S")
    index_split = cleaned_df[cleaned_df["ds"]==datetime_split].index[0]
    df_train = cleaned_df.iloc[:index_split]
    df_test = cleaned_df.iloc[index_split:]
    #y_test = pd.DataFrame(df_test["y"])

    # since we experienced negative predictions, we want to use a logistic growth model including a floor and a cap
    #df_train["floor"] = 0
    #df_train["cap"] = 500

    # Define the date for which you want predictions (at 6am of day before)
    weather_split_date = pd.Timestamp(str(prediction_date-timedelta(days=1)) + " 06:00:00+00:00")

    # Filter the dataframe based on criteria (weather prediction from midnight the day before, for the next day between 12 and 22)
    filtered_predictions = weather_forecast_df[
        (weather_forecast_df['forecast dt iso'] == weather_split_date) &
        (weather_forecast_df['ds'].dt.date == (weather_split_date + pd.Timedelta(days=1)).date()) &
        (weather_forecast_df['ds'].dt.hour >= 12) & (weather_forecast_df['ds'].dt.hour <= 22)
    ]

    #Instatiating  the model
    m = Prophet(changepoint_prior_scale = 0.5, seasonality_prior_scale = 0.1)

    #Adding regressors/features
    m.add_regressor("temp")
    m.add_regressor("humidity")
    m.add_regressor("wind_speed")
    m.add_regressor("rain_1h")
    m.add_regressor("clouds_all")

    m.fit(df_train)

    #Creating future dataframe
    # Extract the last date from the dataframe
    last_date = df_train["ds"].dt.date.iloc[-1]

    # Construct the desired date range for the next day
    next_day = last_date + pd.Timedelta(days=1)
    desired_time_range = pd.date_range(start=f"{next_day} 12:00:00", end=f"{next_day} 22:00:00", freq='H')

    # Append this to the original dataframe to get the future dataframe
    #future = df_train.append(pd.DataFrame({"ds": desired_time_range}), ignore_index=True)

    # Concatenate the two DataFrames vertically
    future = pd.concat([df_train, pd.DataFrame({"ds": desired_time_range})], ignore_index=True)
    future = future[["ds"]]

    #Updating weather data with predicted weather data
    future['ds'] = future['ds'].dt.tz_localize(None)
    filtered_predictions['ds'] = filtered_predictions['ds'].dt.tz_localize(None)

    future = pd.merge(future,filtered_predictions,how="left")
    #future["floor"] = 0
    #future["cap"] = 500
    future = future.tail(11)
    future = future.drop(columns=['forecast dt iso']).reset_index(drop=True)

    #PREDICTING

    fcst = m.predict(future)

    one_day_forecast = fcst.tail(horizon)
    one_day_forecast = one_day_forecast[one_day_forecast['ds'].dt.date == pd.to_datetime(split_date).date()]
    one_day_forecast_slim = one_day_forecast[["ds","yhat_lower","yhat","yhat_upper"]]
    prediction_forecast = one_day_forecast_slim.merge(df_test[['ds', 'y']], on='ds', how='left')
    prediction_forecast.rename(columns={'y': 'y_true'}, inplace=True)
    prediction_forecast = prediction_forecast.fillna(0)
    prediction_forecast["error"]=prediction_forecast["yhat"]-prediction_forecast["y_true"]
    prediction_forecast["me%"]= prediction_forecast["error"]  / prediction_forecast["y_true"] * 100
    prediction_forecast["yhat_lower"] = prediction_forecast["yhat_lower"].apply(lambda x: 0 if x < 0 else x)
    prediction_forecast["yhat"] = prediction_forecast["yhat"].apply(lambda x: 0 if x < 0 else x)


    return prediction_forecast
