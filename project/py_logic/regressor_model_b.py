import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from prophet import Prophet
from .preprocess_b import preprocess_complete
import pandas as pd
import os
import io


def regressor_model(prediction_date):

    #Load feature dataframe
    feature_df = preprocess_complete()
    #Merge dataframes on ds
    #df = pd.merge(df,feature_df,how="left")
    #Loading weather prediction data
    weather_forecast = pd.read_csv("feature_data/finall_pred_weather.csv")
    weather_forecast["ds"] = pd.to_datetime(weather_forecast["ds"])
    weather_forecast["forecast dt iso"] = pd.to_datetime(weather_forecast["forecast dt iso"])
    feature_df['cap'] = 1.2 * feature_df['y'].max()

    #Setting variables
    horizon = 16

    #Splitting the data
    split_date = str(prediction_date)
    #index_split = merged_df[merged_df["ds"]==split_date].index[0]

    indices = feature_df[feature_df["ds"]==split_date].index

    # If the indices list is empty, return a message
    if len(indices) == 0:
        return False

    index_split = indices[0]

    df_train = feature_df.iloc[:index_split]
    df_test = feature_df.iloc[index_split:]
    y_test = pd.DataFrame(df_test["y"])
    weather_index_split = weather_forecast[weather_forecast["forecast dt iso"]==split_date].index[0]
    weather_predict = weather_forecast.iloc[weather_index_split:weather_index_split+horizon,:]
    weather_predict = weather_predict.drop(columns="forecast dt iso")

    #Instatiating  the model
    m = Prophet(growth = 'logistic', changepoint_prior_scale = 0.1, seasonality_prior_scale = 0.1, seasonality_mode='multiplicative',\
           yearly_seasonality= 12, weekly_seasonality = True)

    #Adding regressors/features
    m.add_regressor("temp")
    m.add_regressor("wind_speed")
    m.add_regressor("wind_deg")
    m.add_regressor("rain")
    m.add_regressor("clouds")
    m.add_regressor("Holiday")
    m.add_regressor("inflation_rate")

    m = m.fit(df_train)

    #Creating future dataframe
    future = m.make_future_dataframe(periods=horizon)
    future['cap'] = 1.2 * feature_df['y'].max()

    #Adding feature values to future dataframe
    future = pd.merge(future,feature_df,how="left")

    #Update Future Timeframe with prediction weather data instead of historical weather data to prevent overfitting
    cols_to_update = ['temp', 'humidity', 'clouds', 'wind_speed', 'wind_deg', 'rain']
    future.loc[future.index[-(horizon):], cols_to_update] = weather_predict[cols_to_update].values

    #Predicting
    forecast = m.predict(future)
    #Clipping low predictions at 200€
    for col in ['yhat', 'yhat_lower', 'yhat_upper']:
        forecast[col] = forecast[col].clip(lower=200.0)

    seven_day_forecast = forecast.tail(horizon)
    seven_day_forecast_slim = seven_day_forecast[["ds","yhat_lower","yhat","yhat_upper"]]
    prediction_forecast = seven_day_forecast_slim
    prediction_forecast["y_true"] = y_test.head(horizon)
    prediction_forecast["error"]=abs(prediction_forecast["yhat"]-prediction_forecast["y_true"])
    prediction_forecast["mae%"]=prediction_forecast["error"] / prediction_forecast["y_true"] * 100

    return prediction_forecast
